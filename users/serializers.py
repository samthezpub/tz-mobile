from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "middle_name",
            "email",
            "is_active",
            "is_staff",
            "created_at",
            "updated_at",
        )


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_repeat = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "middle_name",
            "email",
            "password",
            "password_repeat",
        )

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password_repeat"]:
            raise serializers.ValidationError(
                {"password_repeat": "Passwords do not match."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_repeat")
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs["email"]
        password = attrs["password"]

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"detail": "Invalid email or password."}
            )

        if not user.check_password(password):
            raise serializers.ValidationError({"detail": "Invalid email or password."})

        if not user.is_active:
            raise serializers.ValidationError({"detail": "User account is inactive."})

        attrs["user"] = user
        return attrs
