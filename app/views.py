from django.shortcuts import render
from django.http import Http404
from django.conf import settings
from django.core import mail
from rest_framework import status, permissions, viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from oauth2_provider.decorators import protected_resource, rw_protected_resource
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope, TokenHasScope
from .models import User, Book, Borrow, BlackListUser, BOOK_STATUS, BookResultsSetPagination
from .serializers import UserSerializer, UserPictureSerializer, BookSerializer, BookStatusSerializer, \
                         BorrowSerializer, BookReturnSerializer, BlackListUserSerializer
from . import helpers
from datetime import datetime, timedelta
import base64, os

# Create your views here.
class UserList(APIView):
    
    permission_classes = [permissions.IsAuthenticated]
    
    parser_classes = (MultiPartParser, FormParser)

    def get(self, req, format=None):
        if User.is_admin(req.user.usertype):
            users = User.objects.all()
            ser = UserSerializer(users, many=True)
            return Response(ser.data)

        return Response(status=status.HTTP_403_FORBIDDEN)

    def post(self, req, format=None):
        if User.is_admin(req.user.usertype):
            dic = User.set(req.data)
            ser = UserSerializer(data=dic)
            if ser.is_valid():
                helpers.ensure_dir(settings.MEDIA_ROOT)
                ser.save()
                return Response(ser.data, status=status.HTTP_201_CREATED)

            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_403_FORBIDDEN)

class UserDelete(APIView):
    
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, req, pk, format=None):
        if User.is_admin(req.user.usertype):
            o = User.get(pk)
            o.delete()
            User.remove_picture(o)
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_403_FORBIDDEN)

class UserDetail(APIView):
    
    permission_classes = [permissions.IsAuthenticated]

    def get_picture_data(self, o):
        h = None
        try:
            k = o.get_picture_path()
            if os.path.exists(k):
                j = open(k, 'rb').read()
                h = base64.b64encode(j)

        except:
            pass

        return h

    def get(self, req, pk, format=None):
        o = User.get(pk)
        ser = UserSerializer(o)
        data = {
            'data': ser.data,
            'picture-data': self.get_picture_data(o)
        }
        return Response(data)

    def put(self, req, pk, format=None):
        o = User.get(pk)
        o.set_password(req.data['password'])
        ser = UserSerializer(o, data=req.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data)

        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

class UserPicture(APIView):
    
    permission_classes = [permissions.IsAuthenticated]
    
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, req, pk, format=None):
        o = User.get(pk)
        ser = UserPictureSerializer(o, data=req.data)
        if ser.is_valid():
            helpers.ensure_dir(settings.MEDIA_ROOT)
            ser.save()
            return Response(ser.data)

        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
    
class BookList(APIView):
    
    def get(self, req, format=None):
        books = Book.objects.all()
        paginator = BookResultsSetPagination()
        pgbooks = paginator.paginate_queryset(books, req)
        ser = BookSerializer(pgbooks, many=True, context={ 'request': req })
        return Response(ser.data)

class BookCreate(APIView):
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, req, format=None):
        if User.is_admin(req.user.usertype) or User.is_librarian(req.user.usertype):
            ser = BookSerializer(data=req.data)
            if ser.is_valid():
                helpers.ensure_dir(settings.MEDIA_ROOT)
                ser.save()
                return Response(ser.data, status=status.HTTP_201_CREATED)

            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_403_FORBIDDEN)

class BookDetail(APIView):

    def get_picture_data(self, o):
        h = None
        try:
            k = os.path.join(settings.MEDIA_ROOT, o.picture.url)
            if os.path.exists(k):
                j = open(k, 'rb').read()
                h = base64.b64encode(j)

        except:
            pass

        return h

    def get(self, req, pk, format=None):
        o = Book.get(pk)
        ser = BookSerializer(o)
        data = {
            'data': ser.data,
            'picture-data': self.get_picture_data(o)
        }
        return Response(data)

class BookDelete(APIView):
    
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, req, pk, format=None):
        if User.is_admin(req.user.usertype):
            o = Book.get(pk)
            o.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_403_FORBIDDEN)

class BookUpdate(APIView):
    
    permission_classes = [permissions.IsAuthenticated]

    def put(self, req, pk, format=None):
        if User.is_admin(req.user.usertype) or User.is_librarian(req.user.usertype):
            o = Book.get(pk)
            ser = BookSerializer(o, data=req.data)
            if ser.is_valid():
                ser.save()
                return Response(ser.data)

            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_403_FORBIDDEN)

class BookStatus(APIView):
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, req, pk, format=None):
        if User.is_admin(req.user.usertype) or User.is_librarian(req.user.usertype):
            o = Book.get(pk)
            ser = BookStatusSerializer(o)
            data = {
                'status': BOOK_STATUS[ser.data['status']]
            }
            return Response(data)

        return Response(status=status.HTTP_403_FORBIDDEN)

    def put(self, req, pk, format=None):
        if User.is_admin(req.user.usertype) or User.is_librarian(req.user.usertype):
            o = Book.get(pk)
            ser = BookStatusSerializer(o, data=req.data)
            if ser.is_valid():
                ser.save()
                return Response(ser.data)

            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_403_FORBIDDEN)

class BookCheckout(APIView):
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, req, book_id, format=None):
        if User.is_admin(req.user.usertype) or User.is_student(req.user.usertype) or \
            User.is_teacher(req.user.usertype) or User.is_librarian(req.user.usertype):
            dic = {
                'user': req.user.id,
                'book': book_id,
                'startdate': datetime.now().date(),
                'enddate': helpers.date3weekslater(datetime.now())
            }
            ser = BorrowSerializer(data=dic)
            if ser.is_valid():
                user = req.user
                book = Book.get(book_id)

                r, m = user.can_borrow(book)

                if r:
                    ser.save()
                    book.status = 2
                    book.save()
                    return Response(ser.data, status=status.HTTP_201_CREATED)

                else:
                    return Response(m, status=status.HTTP_400_BAD_REQUEST)

            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_403_FORBIDDEN)

class BookReturn(APIView):
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, req, book_id, format=None):
        if User.is_admin(req.user.usertype) or User.is_student(req.user.usertype) or \
            User.is_teacher(req.user.usertype) or User.is_librarian(req.user.usertype):
            dic = {
                'user': req.user.id
            }
            ser = BookReturnSerializer(data=dic)
            if ser.is_valid():
                user = req.user
                book = Book.get(book_id)
                borrow = Borrow.objects.filter(user=user).filter(book=book)[0]
                book.status = 3
                book.save()
                borrow.delete()
                if borrow.enddate <= datetime.now().date():
                    if user.returnbooknotontime is not None:
                        user.returnbooknotontime = user.returnbooknotontime + 1

                    else:
                        user.returnbooknotontime = 1

                    user.save()
                    if user.returnbooknotontime >= 5:
                        o, created = BlackListUser.objects.get_or_create(user=user)

                return Response(ser.data, status=status.HTTP_201_CREATED)

            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_403_FORBIDDEN)

class Daily(APIView):
    
    def get(self, req, format=None):
        con = None
        res = None

        try:
            ls = Borrow.objects.filter(enddate=datetime.now() + timedelta(days=2)).all()
            la = Borrow.objects.filter(enddate=datetime.now() + timedelta(days=1)).all()
            lx = Borrow.objects.filter(enddate__lte=datetime.now()).all()

            con = mail.get_connection()
            con.open()

            for o in ls:
                user = o.user
                book = o.book
                user.email_user('The book {0} that you have borrowed will be expired on {1}'.format(book.title, o.enddate), 
                                'Please return the book ASAP', 
                                con, settings.SERVER_EMAIL)

            for o in la:
                user = o.user
                book = o.book
                user.email_user('The book {0} that you have borrowed will be expired on {1}'.format(book.title, o.enddate), 
                                'Please return the book ASAP', 
                                con, settings.SERVER_EMAIL)

            for o in lx:
                user = o.user
                book = o.book
                if book.status != 4:
                    book.status = 4
                    book.save()

                user.email_user('The book {0} that you have borrowed has expired'.format(book.title), 
                                'Please return the book ASAP', 
                                con, settings.SERVER_EMAIL)

            res = Response({ 'success': 1 })

        except Exception as e:
            res = Response({ 'error': 1, 'message': str(e) })

        finally:
            if con is not None:
                con.close()

        return res

class BlackListUserList(APIView):
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, req, format=None):
        if User.is_admin(req.user.usertype):
            ls = BlackListUser.objects.all()
            ser = BlackListUserSerializer(ls, many=True)
            return Response(ser.data)

        return Response(status=status.HTTP_403_FORBIDDEN)

    def post(self, req, format=None):
        if User.is_admin(req.user.usertype):
            ser = BlackListUserSerializer(data=req.data)
            if ser.is_valid():
                ser.save()
                return Response(ser.data, status=status.HTTP_201_CREATED)

            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_403_FORBIDDEN)

class BlackListUserDetail(APIView):
    
    permission_classes = [permissions.IsAuthenticated]

    def get(self, req, pk, format=None):
        if User.is_admin(req.user.usertype):
            o = BlackListUser.get(pk)
            ser = UserSerializer(o.user)
            return Response(ser.data)

        return Response(status=status.HTTP_403_FORBIDDEN)

    def put(self, req, pk, format=None):
        if User.is_admin(req.user.usertype):
            o = BlackListUser.get(pk)
            ser = BlackListUserSerializer(o, data=req.data)
            if ser.is_valid():
                ser.save()
                return Response(ser.data)

            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_403_FORBIDDEN)

    def delete(self, req, pk, format=None):
        if User.is_admin(req.user.usertype):
            o = BlackListUser.get(pk)
            o.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_403_FORBIDDEN)