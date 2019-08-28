# -*- coding: utf-8 -*-

import grokcore.component as grok

from megrok import pagetemplate as pt
from zeam.form import base
from zeam.form.base import Actions
from zeam.form.base.widgets import getWidgetExtractor
from zeam.form.composed import SubForm
from zeam.form.layout import ComposedForm
from zope.interface import implementer

from dolmen.forms.wizard import MF as _
from dolmen.forms.wizard.interfaces import IWizard
from dolmen.forms.wizard.actions import (PreviousAction, SaveAction,
    NextAction, HiddenSaveAction)


pt.templatedir('default_templates')


@implementer(IWizard)
class Wizard(ComposedForm):  
    grok.baseclass()

    ignoreRequest = True
    ignoreContent = False

    fields = base.Fields(base.Field("Step"))
    fields['step'].mode = base.HIDDEN
    fields['step'].defaultValue = 0

    actions = base.Actions(
        PreviousAction(_(u"Back")),
        SaveAction(_(u"Save")),
        NextAction(_(u"Continue")))

    def __init__(self, context, request):
        super(Wizard, self).__init__(context, request)
        self.setContentData(self)
        self.allSubforms = list(self.allSubforms)
        self.__extracted_step = False

    def finish(self):
        """After-save hook.
        """
        return

    def getMaximumStepId(self):
        """Returns the maximum step id.
        """
        return len(self.allSubforms) - 1

    def getCurrentStepId(self):
        """Returns the current step id.
        """
        if self.__extracted_step is True:
            return int(self.step)

        value, error = getWidgetExtractor(
            self.fields['step'], self, self.request).extract()

        if value is base.NO_VALUE:
            value = 0
        else:
            value = int(value)

        if value < 0 or value > self.getMaximumStepId():
            value = 0
        self.step = value
        self.__extracted_step = True
        return value

    def setCurrentStep(self, sid):
        """Sets a new current step.
        """
        sid = int(sid)
        if not self.allSubforms:
            self.current = None
            self.step = sid
        else:
            try:
                assert sid >= 0 and sid < len(self.allSubforms)
            except AssertionError as e:
                raise AssertionError(
                    'Value %r is not within the permitted range' % sid)
            self.step = sid
            self.current = self.allSubforms[sid]

    def updateForm(self):
        self.setCurrentStep(self.getCurrentStepId())
        base.Form.updateActions(self)
        self.current.updateWidgets()
        base.Form.updateWidgets(self)

    def update(self):
        pass


class WizardTemplate(pt.PageTemplate):
    pt.view(Wizard)


class WizardStep(SubForm):
    pt.view(Wizard)
    grok.baseclass()

    #ignoreContent = False
    actions = Actions(
        HiddenSaveAction(_(u"Save")))


__all__ = ["Wizard", "WizardStep", "Fields",
           "Action", "Actions", "FAILURE", "SUCCESS"]
