from django.db import models
from .base import BaseModel
from akp_accounts.models import CustomUser
from Base.base import HomeBaseModel
from django.utils import timezone
from datetime import timedelta
from django_ckeditor_5.fields import CKEditor5Field
from django.urls import NoReverseMatch, reverse
from Base.helpers import optimize_image

from django.core.exceptions import ValidationError

class NewsTagBanner(BaseModel):
    tag_name = models.CharField(max_length=100, null=True, blank=True)
    news_link = models.URLField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.tag_name

class NewsCategory(BaseModel):
    name = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(max_length=100, null=True, blank=True, unique=True)
    description = models.TextField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0, null=True, blank=True)

    class Meta:
        verbose_name_plural = "News Categories"
        ordering = ['-order']
    
    def get_total_category(self):
        return self.news.count()

    def __str__(self):
        return self.name
    
class NewsSubCategory(BaseModel):
    name = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(max_length=100, null=True, blank=True, unique=True)
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(NewsCategory, on_delete=models.CASCADE, related_name='subcategories')

    def get_total_subcategory(self):
        return self.news.count()

    def __str__(self):
        return self.name

class AboutUs(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    content = CKEditor5Field(config_name='extends', null=True, blank=True)

    class Meta:
        verbose_name_plural = "About Us"

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if len(self.content) < 5:
            raise ValidationError({
                'content': "Content must be at least 5 characters long."
            })
        super().save(*args, **kwargs)

class NewsTag(BaseModel):
    name = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(max_length=100, null=True, blank=True, unique=True)

    def get_total_tag(self):
        return self.news.count()

    def __str__(self):
        return self.name

class News(HomeBaseModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, help_text="Unique URL slug for the article. Use only alphanumeric characters, underscores, and hyphens. Example: 'my-article-title'.")
    content = CKEditor5Field(config_name='extends', null=True, blank=True, help_text="Content of the article.")
    summary = models.TextField(blank=True, help_text="Short summary of the article (max 200 characters)")
    featured_image = models.ImageField(upload_to='news_images_v2/', help_text="Upload a featured image for this article (Recommended size: 16:9)", null=True, blank=True)
    featured_video = models.CharField(max_length=100, null=True, blank=True, help_text="YouTube or Vimeo link for featured video (Recommended Link Format: VIDEO_ID Only)")
    
    # Publishing information
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='articles', help_text="Author of the article")
    category = models.ForeignKey(NewsCategory, on_delete=models.CASCADE, related_name='news', help_text="Category of the article", null=True, blank=True)
    subcategory = models.ForeignKey(NewsSubCategory, on_delete=models.CASCADE, related_name='news', help_text="Subcategory of the article", null=True, blank=True)
    tags = models.ManyToManyField(NewsTag, related_name='news', blank=True, help_text="Tags associated with the article")
    
    # Metadata
    published_at = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "News Articles"
        ordering = ['-published_at']

    def get_total_comments(self):
        return self.comments.filter(is_approved=True).count()
    
    def clean(self, *args, **kwargs):
        if self.category and self.subcategory:
            raise ValidationError({
                'subcategory': "You cannot select both a category and a subcategory. Please choose one."
            })
        if not self.title:
            raise ValidationError({
                'title': "Title cannot be empty."
            })
        if not self.content:
            raise ValidationError({
                'content': "Content cannot be empty."
            })
        if not self.slug:
            raise ValidationError({
                'slug': "Slug cannot be empty."
            })
        if self.featured_image and self.featured_video:
            raise ValidationError(
                "You can only provide a featured image OR a featured video, not both."
            )
        if self.featured_image and not self.featured_image.name.endswith(('.jpg', '.jpeg', '.png', '.webp')):
            raise ValidationError({
                'featured_image': "Featured image must be a valid image file (jpg, jpeg, png, webp)."
            })
        super().clean(*args, **kwargs)

    def get_absolute_url(self):
        try:
            if hasattr(self, 'slug') and self.slug:
                return reverse('news_details', kwargs={'slug': self.slug})
        except NoReverseMatch:
            return "#"
        return "#"
    

    def time_since_published(self):
        
        if not self.published_at:
            return "unpublished"

        now = timezone.now()
        diff = now - self.published_at

        # seconds
        seconds = diff.total_seconds()
        if seconds < 60:
            return "just now" if seconds < 5 else f"{int(seconds)} seconds ago"

        # minutes
        minutes = seconds / 60
        if minutes < 60:
            m = int(minutes)
            return f"{m} min{'s' if m != 1 else ''} ago"

        # hours
        hours = minutes / 60
        if hours < 24:
            h = int(hours)
            return f"{h} hour{'s' if h != 1 else ''} ago"

        # days
        days = diff.days
        if days < 30:
            return f"{days} day{'s' if days != 1 else ''} ago"

        # months (approximate)
        months = days // 30
        if months < 12:
            return f"{months} month{'s' if months != 1 else ''} ago"

        # years
        years = days // 365
        return f"{years} year{'s' if years != 1 else ''} ago"
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # if self.slug:
        #     try:
        #         old_instance = News.objects.get(slug=self.slug)
        #         if old_instance.featured_image != self.featured_image:
        #             optimized_image = optimize_image(self.featured_image)
        #             if optimized_image:
        #                 self.featured_image = optimized_image
        #             else:
        #                 self.featured_image = old_instance.featured_image
        #             super().save(*args, **kwargs)
        #             return
        #     except News.DoesNotExist:
        #         pass
        # Optimize the featured image if it exists
        try:
            old_instance = News.objects.get(slug=self.slug)
            image_changed = old_instance.featured_image != self.featured_image
        except News.DoesNotExist:
            image_changed = True
        if image_changed and self.featured_image:
            optimized_image = optimize_image(self.featured_image)
            if optimized_image:
                self.featured_image = optimized_image
        super().save(*args, **kwargs)
    

class ViewCountNews(BaseModel):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='view_counts')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    count = models.PositiveIntegerField(default=0)
    ip_addr = models.CharField(max_length=50, null=True, blank=True)
    impressions = models.PositiveIntegerField(default=0)
    total_clicks = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('news', 'ip_addr')

    def __str__(self):
        return f"Total {self.count} View count for {self.news.title}"

class NewsHomeBanner(BaseModel):
    banner_title = models.CharField(max_length=100, null=True, blank=True)
    banner_news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='banner_news')
    banner_image = models.ImageField(upload_to='banner_images/', null=True, blank=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.banner_title

class NewsComment(BaseModel):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='news_comments')
    content = models.TextField()
    
    # Self-referential relationship for nested comments
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    # Moderation
    is_approved = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']

    def time_since_published(self):
        
        if not self.created_at:
            return "unpublished"

        now = timezone.now()
        diff = now - self.created_at

        # seconds
        seconds = diff.total_seconds()
        if seconds < 60:
            return "just now" if seconds < 5 else f"{int(seconds)} seconds ago"

        # minutes
        minutes = seconds / 60
        if minutes < 60:
            m = int(minutes)
            return f"{m} min{'s' if m != 1 else ''} ago"

        # hours
        hours = minutes / 60
        if hours < 24:
            h = int(hours)
            return f"{h} hour{'s' if h != 1 else ''} ago"

        # days
        days = diff.days
        if days < 30:
            return f"{days} day{'s' if days != 1 else ''} ago"

        # months (approximate)
        months = days // 30
        if months < 12:
            return f"{months} month{'s' if months != 1 else ''} ago"

        # years
        years = days // 365
        return f"{years} year{'s' if years != 1 else ''} ago"
    
    def __str__(self):
        return f"Comment by {self.author.get_full_name() if hasattr(self.author, 'get_full_name') else self.author.username} on {self.news.title}"
    
    # @property
    # def is_reply(self):
    #     """Check if this comment is a reply to another comment."""
    #     return self.parent is not None
    
    # @property
    # def get_replies(self):
    #     """Get all replies to this comment."""
    #     return self.replies.filter(is_approved=True)


class LiveUpdates(BaseModel):
    title = models.CharField(max_length=255)
    slug = models.ForeignKey(News, on_delete=models.CASCADE, null=True, blank=True, related_name="live_updates")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Live Updates"

    def __str__(self):
        return self.title

class SocialAccount(models.Model):
    facebook = models.URLField(null=True, blank=True)
    twitter = models.URLField(null=True, blank=True)
    instagram = models.URLField(null=True, blank=True)
    youtube = models.URLField(null=True, blank=True)
    class Meta:
        verbose_name_plural = "Social Accounts"

    def __str__(self):
        return f"Social Accounts"


class Advertisements(BaseModel):
    BANNER_SIZES = (
        ('Home Banner 640x926', 'Home Banner 640x926'),
        ('Home Banner 2496x300', 'Home Banner 2496x300'),
        ('News Article Banner 600x700', 'News Article Banner 600x700'),
    )
    banner_title = models.CharField(max_length=100, null=True, blank=True)
    banner_link = models.URLField(null=True, blank=True)
    banner_image = models.ImageField(upload_to='banner_images/', null=True, blank=True)
    banner_size = models.CharField(max_length=50, null=True, blank=True, choices=BANNER_SIZES)
    is_active = models.BooleanField(default=True, null=True, blank=True)
    
    def __str__(self):
        return self.banner_title or f"Advertisement {self.id}"