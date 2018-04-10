from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.core import mail
from django.http import Http404
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework.pagination import PageNumberPagination
from datetime import datetime
import os

BOOK_STATUS = {
    1: 'available',
    2: 'borrowed',
    3: 'returned',
    4: 'expired'
}

# Create your models here.
def user_dir_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.userid, filename)

class BookResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 1000

class User(AbstractBaseUser, PermissionsMixin):
    userid = models.CharField(_('userid'), max_length=50, unique=True, db_index=True)
    username = models.CharField(_('username'), max_length=50, unique=True, db_index=True)
    email = models.EmailField(_('email address'), max_length=255, unique=True, db_index=True)
    usertype = models.SmallIntegerField()
    is_active = models.BooleanField(_('active'), default=True)
    mobile = models.CharField(_('mobile'), max_length=20, blank=True, null=True)
    firstname = models.CharField(_('firstname'), max_length=100)
    lastname = models.CharField(_('lastname'), max_length=100)
    picture = models.ImageField(max_length=67200, upload_to=user_dir_path, blank=True, null=True)
    returnbooknotontime = models.IntegerField(blank=True, null=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['userid', 'email', 'usertype', 'firstname', 'lastname']
    
    objects = UserManager()
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        
    def email_user(self, subject, message, con, from_email=None):
        x = mail.EmailMessage(
            subject,
            message,
            from_email,
            [self.email],
            connection=con
        )
        x.send()

    def get_picture_dir(self):
        k = None
        try:
            k = os.path.join(settings.MEDIA_ROOT, 'user_{0}'.format(self.userid))

        except:
            pass

        return k

    def get_picture_path(self):
        k = None
        try:
            k = os.path.join(settings.MEDIA_ROOT, self.picture.url)

        except:
            pass

        return k

    def get_max_borrow(self):
        r = 0
        if self.usertype == 1:
            r = 2

        elif self.usertype in [2, 3]:
            r = 3

        return r

    def can_borrow(self, book):
        n = self.get_max_borrow()
        i = Borrow.objects.filter(user=self).count()
        j = Borrow.objects.filter(book=book).count()
        b = self.is_blacklisted()
        e = self.is_borrow_expired()
        r = False
        m = {}

        if i < n and j == 0 and b == False and e == False:
            r = True

        elif i == n:
            m = { 'error': 1, 'message': 'max borrow limit has reached' }

        elif j > 0 or book.is_borrowed():
            m = { 'error': 1, 'message': 'already borrowed' }

        elif b:
            m = { 'error': 1, 'message': 'already black-listed' }

        elif e:
            m = { 'error': 1, 'message': 'some books already expired' }

        return r, m

    def is_blacklisted(self):
        n = BlackListUser.objects.filter(user=self).count()
        return True if n > 0 else False

    def is_borrow_expired(self):
        n = Borrow.objects.filter(user=self).filter(enddate__lte=datetime.now()).count()
        return True if n > 0 else False

    def __str__(self):
        return '{0} - {1} {2}'.format(self.userid, self.firstname, self.lastname)
        
    def __unicode__(self):
        return '{0} - {1} {2}'.format(self.userid, self.firstname, self.lastname)

    @classmethod
    def is_admin(cls, i):
        return True if i == 0 else False

    @classmethod
    def is_student(cls, i):
        return True if i == 1 else False

    @classmethod
    def is_teacher(cls, i):
        return True if i == 2 else False

    @classmethod
    def is_librarian(cls, i):
        return True if i == 3 else False

    @classmethod
    def remove_picture(cls, o):
        k = o.get_picture_path()
        h = o.get_picture_dir()
        if os.path.exists(k):
            os.remove(k)

        if os.path.exists(h):
            os.rmdir(h)

    @classmethod
    def get(cls, pk):
        try:
            return User.objects.get(pk=pk)

        except User.DoesNotExist:
            raise Http404

    @classmethod
    def get_userid(cls, userid, usertype):
        r = cls.get_userid_prefix(int(usertype))
        s = '{0}{1}'.format(r, userid)
        return s

    @classmethod
    def get_userid_prefix(cls, type):
        r = ''
        if type == 1: #student
            r = 'X'

        elif type == 2: #teacher
            r = 'Y'

        elif type == 3: #librarian
            r = 'Z'

        return r

    @classmethod
    def set(cls, m):
        dic = m.copy()
        dic['is_active'] = True
        dic['userid'] = cls.get_userid(dic['userid'], dic['usertype'])
        return dic

def book_dir_path(instance, filename):
    return 'isbn_{0}/{1}'.format(instance.isbn, filename)

class Book(models.Model):
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    publisher = models.CharField(max_length=200)
    edition = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    picture = models.ImageField(max_length=21376, upload_to=book_dir_path, blank=True, null=True)
    barcode = models.CharField(max_length=200, unique=True)
    status = models.SmallIntegerField()

    def get_picture_dir(self):
        k = None
        try:
            k = os.path.join(settings.MEDIA_ROOT, 'isbn_{0}'.format(self.isbn))

        except:
            pass

        return k

    def get_picture_path(self):
        k = None
        try:
            k = os.path.join(settings.MEDIA_ROOT, self.picture.url)

        except:
            pass

        return k

    @classmethod
    def remove_picture(cls, o):
        k = o.get_picture_path()
        h = o.get_picture_dir()
        if os.path.exists(k):
            os.remove(k)

        if os.path.exists(h):
            os.rmdir(h)

    @classmethod
    def get(cls, pk):
        try:
            return Book.objects.get(pk=pk)

        except Book.DoesNotExist:
            raise Http404

    def is_borrowed(self):
        return self.status == 2

class Borrow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    startdate = models.DateField()
    enddate = models.DateField()

class BlackListUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.ForeignKey)

    @classmethod
    def get(cls, pk):
        try:
            return BlackListUser.objects.get(pk=pk)

        except BlackListUser.DoesNotExist:
            raise Http404