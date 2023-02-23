import os
import uuid

from django import forms

from tasks.models import TaskInstance


class CompleteTaskForm(forms.ModelForm):
    class Meta:
        model = TaskInstance
        fields = ['photo', 'note']

    photo = forms.ImageField(required=True, help_text="Required.", label="Photo of completed task")
    note = forms.CharField(required=False, help_text="Optional.", label="Extra notes")

    def save(self, commit=True):
        task_instance = super().save(commit=False)
        task_instance.photo.name = uuid.uuid4().hex + os.path.splitext(task_instance.photo.name)[1]
        task_instance.report_task_complete()
        if commit:
            task_instance.save()
        return task_instance
