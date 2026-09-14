from django.db import migrations, models
import cinema.youtube

def copy_links(apps,schema_editor):
    Movie = apps.get_model('cinema','Movie')
    for movie in Movie.objects.exclude(youtube_id='').iterator():
        movie.youtube_url = 'https://www.youtube.com/watch?v=' + movie.youtube_id
        movie.save(update_fields=['youtube_url'])

def copy_ids(apps,schema_editor):
    Movie = apps.get_model('cinema','Movie')
    for movie in Movie.objects.exclude(youtube_url='').iterator():
        movie.youtube_id = cinema.youtube.youtube_video_id(movie.youtube_url)
        movie.save(update_fields=['youtube_id'])

class Migration(migrations.Migration):
    dependencies = [('cinema','0001_initial')]
    operations = [
        migrations.AddField(model_name='movie',name='youtube_url',field=models.URLField('YouTube trailer link',blank=True,max_length=500,validators=[cinema.youtube.validate_youtube_url],help_text='Paste the YouTube watch or share link. Uploaded video takes priority; clear the upload to use this link.')),
        migrations.RunPython(copy_links,copy_ids),
        migrations.RemoveField(model_name='movie',name='youtube_id'),
    ]
