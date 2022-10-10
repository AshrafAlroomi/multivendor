from rest_framework import serializers

from accounts.models import Profile, BankAccount


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id',
                  'mobile_number',
                  'bio',
                  'display_name',
                  'address',
                  'city',
                  'post_code',
                  'country',
                  'state',
                  'status',
                  'code',
                  'recommended_by',
                  'referrals',
                  'blance',
                  'requested',
                  'date',
                  'date_update',
                  'slug',
                  'image')


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = ('id', 'vendor_profile',
                  'bank_name', 'account_number', 'swift_code', 'account_name',
                  'country',
                  'paypal_email',
                  'description',
                  'date',
                  'date_update',
                  )
