import os
import uuid

def generate_unique_filename(filename):
    ext = os.path.splitext(filename)[1]
    new_filename = str(uuid.uuid4()) + ext
    return new_filename


def submission_file_path(instance, filename):
    return f'submissions/{instance.work_submission.pk}/{filename}'