from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.functions import ExtractWeek, ExtractYear
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings

from .models import Entry
from .permissions import EntryAccessPermission, UserAccessPermission
from .serializers import EntrySerializer, SignupSerializer, UserSerializer

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


def user_data(user):
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.profile.role,
    }


class LoginView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        user = authenticate(
            request,
            username=request.data.get('username', ''),
            password=request.data.get('password', ''),
        )
        if user is None:
            return Response({'detail': 'Invalid username or password.'}, status=status.HTTP_401_UNAUTHORIZED)
        login(request, user)
        return Response({
            'token': jwt_encode_handler(jwt_payload_handler(user)),
            **user_data(user),
        })


class SignupView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = SignupSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user = User.objects.get(pk=response.data['id'])
        return Response(user_data(user), status=response.status_code)


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (UserAccessPermission,)
    queryset = User.objects.select_related('profile').all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        return SignupSerializer if self.action == 'create' else UserSerializer


class EntryViewSet(viewsets.ModelViewSet):
    serializer_class = EntrySerializer
    permission_classes = (EntryAccessPermission,)

    def get_queryset(self):
        queryset = Entry.objects.select_related('user', 'user__profile').order_by('-date', '-id')
        if self.request.user.profile.role != 'ADMIN':
            queryset = queryset.filter(user=self.request.user)
        from_date = self.request.query_params.get('from')
        to_date = self.request.query_params.get('to')
        if from_date:
            queryset = queryset.filter(date__gte=from_date)
        if to_date:
            queryset = queryset.filter(date__lte=to_date)
        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        target_user_id = serializer.validated_data.pop('user_id', None)
        if user.profile.role == 'ADMIN' and target_user_id:
            user = User.objects.get(pk=target_user_id)
        serializer.save(user=user)

    def perform_update(self, serializer):
        serializer.save(user=self.get_object().user)


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def weekly_report(request):
    queryset = Entry.objects.all()
    if request.user.profile.role != 'ADMIN':
        queryset = queryset.filter(user=request.user)
    from_date = request.query_params.get('from')
    to_date = request.query_params.get('to')
    if from_date:
        queryset = queryset.filter(date__gte=from_date)
    if to_date:
        queryset = queryset.filter(date__lte=to_date)
    report = queryset.annotate(year=ExtractYear('date'), week=ExtractWeek('date')).values(
        'year', 'week'
    ).annotate(total_distance=Sum('distance'), total_duration=Sum('duration')).order_by('year', 'week')
    return Response([
        {
            'year': row['year'],
            'week': row['week'],
            'total_distance': row['total_distance'],
            'total_duration': row['total_duration'],
            'average_speed': round(row['total_distance'] / row['total_duration'], 2)
            if row['total_duration'] else 0,
        }
        for row in report
    ])


WeeklyReport = weekly_report
