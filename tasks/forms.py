import os
import uuid

from django import forms

from tasks.models import TaskInstance


class CompleteTaskForm(forms.ModelForm):
    """
    Form for a user to complete a task.
    Allows a user to upload a photo and add a note about the task.
    """
    class Meta:
        model = TaskInstance
        fields = ['photo', 'note']

    photo = forms.ImageField(required=True, help_text="Required.", label="Photo of completed task")
    note = forms.CharField(required=False, help_text="Optional.", label="Extra notes")

    def save(self, commit=True):
        """
        Mark the task as Pending Approval and save the photo with a random UUID filename.
        """
        task_instance = super().save(commit=False)
        # Rename the photo to a random UUID to avoid collisions
        task_instance.photo.name = uuid.uuid4().hex + os.path.splitext(task_instance.photo.name)[1]
        task_instance.report_task_complete()
        if commit:
            task_instance.save()
        return task_instance
