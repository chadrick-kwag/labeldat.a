from django.db import models
from django.views import generic
from django.urls import reverse

# Create your models here.

class Dataset(models.Model):
    """
    Model representing a book genre (e.g. Science Fiction, Non Fiction).
    """
    dsid =models.IntegerField(unique=True,null=False)
    title = models.CharField(max_length=200, null=False,help_text="enter title for dataset")
    description = models.TextField()
    thumbnail_filename = models.ImageField(null=True,upload_to='datasets/thumbnails/')
    label_jsonfile = models.FileField(null=True,upload_to='datasets/labeljson/')

    
    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return str(self.dsid)

    def get_dataset_info_url(self):
        return reverse('dsinfopage',kwargs={"dsid":str(self.dsid)})


class DatasetListView(generic.ListView):
	model = Dataset
	template_name = 'dataset_listview.html'

class save_progress(models.Model):

	username=models.CharField(max_length=50,null=False)
	dsid = models.IntegerField(null=False)
	savefile=models.FileField(null=False,upload_to='saves')


class recent_activity(models.Model):

	userid = models.IntegerField(null=False)
	dataset = models.ForeignKey(Dataset,on_delete=models.CASCADE)
	access_datetime = models.DateTimeField(auto_now=True)

	

