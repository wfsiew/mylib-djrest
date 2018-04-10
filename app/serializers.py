from rest_framework import routers, serializers
from .models import User, Book, Borrow, BlackListUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'userid', 'username', 'usertype', 'email', 'is_active', 'mobile', 'firstname', 
                  'lastname', 'picture', 'returnbooknotontime')

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.set_password(validated_data.get('password'))
        user.save()
        return user

class UserPictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('picture',)

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ('author', 'isbn', 'title', 'description', 'publisher', 'edition', 
                  'category', 'picture', 'barcode', 'status')

class BookStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ('status',)

class BorrowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrow
        fields = ('user', 'book', 'startdate', 'enddate')

class BookReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrow
        fields = ('user',)

class BlackListUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlackListUser
        fields = ('user',)