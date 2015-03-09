import django_filters
from dateutil import parser
from django.contrib.auth.models import Group
from appsdir.knowledgebase.models import Category, Tag, Article
from appsdir.support.models import Ticket, Post, Queue, Macro
from appsdir.announcements.models import Announcement
from appsdir.companies.models import Company
from appsdir.contacts.models import Contact
from appsdir.loggers.models import AuthenticationLogger
from rest_framework import serializers, status, viewsets, filters, routers, permissions, parsers
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import DjangoModelPermissions, IsAdminUser
from rest_framework.response import Response
from actstream.models import Action
from actstream import action


class StaffRW_UserR_Permission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        else:
            if request.method == 'GET':
                return True
            else:
                return False

class StaffRW_SelfRW_CompanyMemberR_Permission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        else:
            if obj == request.user:
                return True
            else:
                if obj.company == request.user.company and request.method == 'GET':
                    return True
                else:
                    return False

class StaffRW_CompanyMemberRW_Permission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        else:
            if obj.author.company == request.user.company:
                return True
            else:
                return False

class Company_StaffRW_CompanyMemberRW_Permission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        else:
            if obj == request.user.company:
                return True
            else:
                return False

def actions_queryset_to_dict(actions_queryset):
    actions_list = []
    for action in actions_queryset:
        tmp = {
            'actor_url': action.actor.get_absolute_url(),
            'actor_object_id': action.actor_object_id,
            'actor_content_type': str(action.actor_content_type).title(),
            'timestamp': str(action.timestamp),
            'description': action.description,
            'verb': action.verb
        }

        if action.target:
            try:
                tmp['target_url'] = action.target.get_absolute_url()
                tmp['target_content_type'] = str(action.target_content_type).title()
                tmp['target_object_id'] = action.target_object_id
            except:
                pass

        actions_list.append(tmp)

    return {
        'count': len(actions_list),
        'results': actions_list
    }

class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action

class ActionViewSet(viewsets.ReadOnlyModelViewSet):
    """ Read Only (ReadOnlyModelViewSet) """
    queryset = Action.objects.all()
    serializer_class = ActionSerializer
    permission_classes = (DjangoModelPermissions,)
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter,)
    order_fields = ('timestamp',)
    filter_fields = ('actor_object_id', 'actor_content_type', 'target_object_id', 'target_content_type',)


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group

class GroupViewSet(viewsets.ModelViewSet):
    """
        Queryset
            Staff: all
        Permissions
            DjangoModelPermissions
            IsAdminUser (Staff only)
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (DjangoModelPermissions,IsAdminUser,)

    def perform_create(self, serializer):
        obj = serializer.save()
        action.send(self.request.user, verb='created', target=obj)

    def perform_update(self, serializer):
        obj = serializer.save()
        action.send(self.request.user, verb='modified', target=obj)

    def perform_delete(self, serializer):
        obj = serializer.save()
        action.send(self.request.user, verb='deleted', target=obj)

    @detail_route(methods=['get'])
    def history(self, request, pk):
        try:
            obj = self.get_object()
            history = obj.history.all()[:10].values()

            return Response(history, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({'data': str(ex)}, status=status.HTTP_400_BAD_REQUEST)


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        exclude = ("changed_by",)

class CompanyViewSet(viewsets.ModelViewSet):
    """
        Queryset
            Customers: restricted to their own company
            Staff: all
        Permissions:
            DjangoModelPermissions
            Company_StaffRW_CompanyMemberRW_Permission
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = (DjangoModelPermissions, Company_StaffRW_CompanyMemberRW_Permission,)

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Company.objects.all()
        else:
            return Company.objects.filter(pk=user.company.pk)

    @detail_route(methods=['get'])
    def history(self, request, pk):
        try:
            obj = self.get_object()
            history = obj.history.all()[:10].values()

            return Response(history, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({'data': str(ex)}, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['get'])
    def actions(self, request, pk):
        try:
            company = Company.objects.get(pk=pk)
            contacts = Contact.objects.filter(company=company)
            actions = actions_queryset_to_dict(Action.objects.filter(actor_object_id__in=contacts)[:10])
            return Response(actions, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({'data': str(ex)}, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['get'])
    def authentications(self, request, pk):
        try:
            auths = []
            for auth in AuthenticationLogger.objects.filter(user_id__in=Contact.objects.filter(company_id=pk))[:10]:
                auths.append({
                    "contact": auth.user.pk,
                    "contact_name": auth.user.get_full_name(),
                    "created": auth.created,
                    "action": auth.action,
                    "ip": auth.ip,
                })

            response = {
                "count": len(auths),
                "results": auths,
            }

            return Response(response, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({'data': str(ex)}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        obj = serializer.save()
        action.send(self.request.user, verb='created', target=obj)

    def perform_update(self, serializer):
        obj = serializer.save()
        action.send(self.request.user, verb='modified', target=obj)

    def perform_delete(self, serializer):
        obj = serializer.save()
        action.send(self.request.user, verb='deleted', target=obj)


class ContactSerializer(serializers.ModelSerializer):
    company_name = serializers.StringRelatedField(source="company")
    groups = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), many=True, required=False)

    class Meta:
        model = Contact
        exclude = ('password',)

class ContactViewSet(viewsets.ModelViewSet):
    """
        Queryset
            Customers: restricted to their own company
            Staff: all
        Permissions:
            DjangoModelPermissions
            StaffRW_SelfRW_CompanyMemberR_Permission
    """
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = (DjangoModelPermissions, StaffRW_SelfRW_CompanyMemberR_Permission,)
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter,)
    filter_fields = ('company',)
    order_fields = ('created', 'email',)

    def get_queryset(self):
        filter = {}
        queryset = Contact.objects.all()

        if not self.request.user.is_staff:
            filter['company'] = self.request.user.company

        queryset = queryset.filter(**filter)

        return queryset

    def perform_create(self, serializer):
        obj = serializer.save()
        obj.set_password(self.request.POST['password'])
        obj.save()

        action.send(self.request.user, verb='created', target=obj)

    def perform_update(self, serializer):
        obj = serializer.save()

        if "password" in self.request.data and len(self.request.data["password"]) > 5:
            obj.set_password(self.request.data["password"])
            obj = serializer.save()

        action.send(self.request.user, verb='modified', target=obj)

    def perform_delete(self, serializer):
        obj = serializer.save()
        action.send(self.request.user, verb='deleted', target=obj)

    @detail_route(methods=['get'])
    def actions(self, request, pk):
        try:
            actions = actions_queryset_to_dict(Action.objects.filter(actor_object_id=pk)[:10])
            return Response(actions, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({'data': str(ex)}, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['get'])
    def authentications(self, request, pk):
        try:
            auths = AuthenticationLogger.objects.filter(user_id=pk)[:10].values()
            response = {
                "count": len(auths),
                "results": auths,
            }

            return Response(response, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({'data': str(ex)}, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['get'])
    def history(self, request, pk):
        try:
            obj = self.get_object()
            history = obj.history.all()[:10].values()

            return Response(history, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({'data': str(ex)}, status=status.HTTP_400_BAD_REQUEST)


class AnnouncementSerializer(serializers.ModelSerializer):
    author_name = serializers.StringRelatedField(source="author.get_full_name", read_only=True)

    class Meta:
        model = Announcement
        exclude = ("changed_by",)

class AnnouncementViewSet(viewsets.ModelViewSet):
    """
        Queryset
            Customers: public announcements where status is True
            Staff: all
        Permissions:
            DjangoModelPermissions
            StaffRW_UserR_Permission
    """
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = (DjangoModelPermissions, StaffRW_UserR_Permission,)
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('author', 'created', 'modified', 'public',)

    def get_queryset(self):
        filter = {}
        queryset = Announcement.objects.all()

        start_date = self.request.QUERY_PARAMS.get('start_date', None)
        end_date = self.request.QUERY_PARAMS.get('end_date', None)

        if start_date is not None:
            filter['created__gte'] = parser.parse(start_date)

        if end_date is not None:
            filter['created__lte'] = parser.parse(end_date)

        if not self.request.user.is_staff:
            filter['public'] = True
            filter['status'] = True

        queryset = queryset.filter(**filter)

        return queryset

    def perform_create(self, serializer):
        obj = serializer.save(author=self.request.user)
        action.send(self.request.user, verb='created', target=obj)

    def perform_update(self, serializer):
        obj = serializer.save()
        action.send(self.request.user, verb='modified', target=obj)

    def perform_delete(self, serializer):
        obj = serializer.save()
        action.send(self.request.user, verb='deleted', target=obj)

    @detail_route(methods=['get'])
    def history(self, request, pk):
        try:
            obj = self.get_object()
            history = obj.history.all()[:10].values()

            return Response(history, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({'data': str(ex)}, status=status.HTTP_400_BAD_REQUEST)


class QueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Queue
        exclude = ("changed_by",)

class QueueViewSet(viewsets.ModelViewSet):
    """
        Queryset
            Staff: all
        Permissions:
            DjangoModelPermissions
            StaffRW_UserR_Permission
    """
    queryset = Queue.objects.all()
    serializer_class = QueueSerializer
    permission_classes = (DjangoModelPermissions, IsAdminUser,)

    def perform_create(self, serializer):
        obj = serializer.save()
        action.send(self.request.user, verb='created', target=obj)

    def perform_update(self, serializer):
        obj = serializer.save()
        action.send(self.request.user, verb='modified', target=obj)

    def perform_delete(self, serializer):
        obj = serializer.save()
        action.send(self.request.user, verb='deleted', target=obj)

    @detail_route(methods=['get'])
    def history(self, request, pk):
        try:
            obj = self.get_object()
            history = obj.history.all()[:10].values()

            return Response(history, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({'data': str(ex)}, status=status.HTTP_400_BAD_REQUEST)


class TicketContactSerializer(serializers.ModelSerializer):
    company = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Contact
        fields = ('id', 'first_name', 'last_name', 'email', 'company',)

class TicketSerializer(serializers.ModelSerializer):
    owner_name = serializers.StringRelatedField(source="owner.get_full_name", read_only=True)
    queue_name = serializers.StringRelatedField(source='queue', read_only=True)
    company = serializers.CharField(source='get_company', read_only=True)
    author_name = serializers.StringRelatedField(source="author", read_only=True)
    contacts = TicketContactSerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        exclude = ("changed_by",)

class TicketViewSet(viewsets.ModelViewSet):
    """
        Queryset
            Customers: tickets authorted by fellow company member
            Staff: all
        Permissions:
            DjangoModelPermissions
            StaffRW_CompanyMemberRW_Permission
    """
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = (DjangoModelPermissions, StaffRW_CompanyMemberRW_Permission,)
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('created', 'modified', 'owner', 'status', 'priority', 'flagged', 'queue', 'difficulty_rating', 'satisfaction_rating', 'due_date', 'author',)

    def get_queryset(self):
        filter = {}
        queryset = Ticket.objects.all()

        if not self.request.user.is_staff:
            filter["author__company"] = self.request.user.company

        start_date = self.request.QUERY_PARAMS.get('start_date', None)
        end_date = self.request.QUERY_PARAMS.get('end_date', None)

        if start_date is not None:
            filter['created__gte'] = parser.parse(start_date)

        if end_date is not None:
            filter['created__lte'] = parser.parse(end_date)

        queryset = queryset.filter(**filter)

        return queryset

    def perform_create(self, serializer):
        obj = serializer.save()
        if obj.author not in obj.contacts.all():
            obj.contacts.add(obj.author)
        obj.save()
        action.send(self.request.user, verb='created', target=obj)

    def perform_update(self, serializer):
        obj = serializer.save()
        action.send(self.request.user, verb='modified', target=obj)

    def perform_delete(self, serializer):
        obj = serializer.save()
        action.send(self.request.user, verb='deleted', target=obj)

    @detail_route(methods=['patch'])
    def contacts(self, request, pk):
        try:
            ticket = self.get_object()
            ticket.contacts.clear()
            contacts = request.data.getlist('contacts')
            ticket.contacts.add(*contacts)
            ticket.save()
            return Response(status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({'data': str(ex)}, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['get'])
    def history(self, request, pk):
        try:
            obj = self.get_object()
            history = obj.history.all()[:10].values()

            return Response(history, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({'data': str(ex)}, status=status.HTTP_400_BAD_REQUEST)


class PostSerializer(serializers.ModelSerializer):
    author_name = serializers.StringRelatedField(source="author.get_full_name", read_only=True)
    author_is_staff = serializers.StringRelatedField(source="author.is_staff", read_only=True)
    tid = serializers.StringRelatedField(source="ticket.tid", read_only=True)

    class Meta:
        model = Post
        exclude = ("changed_by",)

class PostViewSet(viewsets.ModelViewSet):
    """
        Queryset
            Customers: visible posts authored by fellow company member
            Staff: all
        Permissions:
            DjangoModelPermissions
            StaffRW_CompanyMemberRW_Permission
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    parser_classes = (parsers.FormParser, parsers.MultiPartParser,)
    permission_classes = (DjangoModelPermissions, StaffRW_CompanyMemberRW_Permission,)
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter,)
    filter_fields = ('ticket', 'created', 'rating', 'modified', 'author',)
    order_fields = ('created', 'rating',)

    def get_queryset(self):
        filter = {}
        queryset = Post.objects.all()

        if not self.request.user.is_staff:
            filter["author__company"] = self.request.user.company
            filter["visible"] = True

        start_date = self.request.QUERY_PARAMS.get('start_date', None)
        end_date = self.request.QUERY_PARAMS.get('end_date', None)

        if start_date is not None:
            filter['created__gte'] = parser.parse(start_date)

        if end_date is not None:
            filter['created__lte'] = parser.parse(end_date)

        queryset = queryset.filter(**filter)

        return queryset

    def perform_create(self, serializer):
        if "author" in self.request.POST and int(self.request.POST["author"]) is not int(self.request.user.id):
            if self.request.user.is_staff:
                obj = serializer.save(author=self.request.user, visible=True, contents="Opened on behalf of Contact %s: <br><br>\"%s\"" % (self.request.POST["author"], self.request.POST["contents"]))
            else:
                raise Exception("Only staff can create posts for different users.")
        else:
            obj = serializer.save(author=self.request.user)

        action.send(self.request.user, verb='created', target=obj)

    def perform_update(self, serializer):
        obj = serializer.save()
        action.send(self.request.user, verb='modified', target=obj)

    def perform_delete(self, serializer):
        obj = serializer.save()
        action.send(self.request.user, verb='deleted', target=obj)

    @detail_route(methods=['get'])
    def history(self, request, pk):
        try:
            obj = self.get_object()
            history = obj.history.all()[:10].values()

            return Response(history, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class MacroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Macro
        exclude = ("changed_by",)

class MacroViewSet(viewsets.ModelViewSet):
    """
        Queryset
            Staff: all
        Permissions:
            DjangoModelPermissions
            IsAdminUser
    """
    queryset = Macro.objects.all()
    serializer_class = MacroSerializer
    permission_classes = (DjangoModelPermissions, IsAdminUser,)
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('author', 'created', 'modified',)

    def perform_create(self, serializer):
        obj = serializer.save(author=self.request.user)
        action.send(self.request.user, verb='created', target=obj)

    def perform_update(self, serializer):
        obj = serializer.save()
        action.send(self.request.user, verb='modified', target=obj)

    def perform_delete(self, serializer):
        obj = serializer.save()
        action.send(self.request.user, verb='deleted', target=obj)

    @detail_route(methods=['get'])
    def history(self, request, pk):
        try:
            obj = self.get_object()
            history = obj.history.all()[:10].values()

            return Response(history, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({'data': str(ex)}, status=status.HTTP_400_BAD_REQUEST)

class KnoweldgebaseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ("changed_by",)

class KnoweldgebaseCategoryViewSet(viewsets.ModelViewSet):
    """
        Queryset
            All
        Permissions:
            DjangoModelPermissions
            IsAdminUser
    """
    queryset = Category.objects.all()
    serializer_class = KnoweldgebaseCategorySerializer
    permission_classes = (DjangoModelPermissions, StaffRW_UserR_Permission,)

    def perform_create(self, serializer):
        obj = serializer.save(author=self.request.user)
        action.send(self.request.user, verb='created', target=obj)

    def perform_update(self, serializer):
        obj = serializer.save()
        action.send(self.request.user, verb='modified', target=obj)

    def perform_delete(self, serializer):
        obj = serializer.save()
        action.send(self.request.user, verb='deleted', target=obj)

    @detail_route(methods=['get'])
    def history(self, request, pk):
        try:
            obj = self.get_object()
            history = obj.history.all()[:10].values()

            return Response(history, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({'data': str(ex)}, status=status.HTTP_400_BAD_REQUEST)

class KnoweldgebaseTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        exclude = ("changed_by",)

class KnoweldgebaseTagViewSet(viewsets.ModelViewSet):
    """
        Queryset
            Staff: all
        Permissions:
            DjangoModelPermissions
            IsAdminUser
    """
    queryset = Tag.objects.all()
    serializer_class = KnoweldgebaseTagSerializer
    permission_classes = (DjangoModelPermissions, IsAdminUser,)

    def perform_create(self, serializer):
        obj = serializer.save(author=self.request.user)
        action.send(self.request.user, verb='created', target=obj)

    def perform_update(self, serializer):
        obj = serializer.save()
        action.send(self.request.user, verb='modified', target=obj)

    def perform_delete(self, serializer):
        obj = serializer.save()
        action.send(self.request.user, verb='deleted', target=obj)

    @detail_route(methods=['get'])
    def history(self, request, pk):
        try:
            obj = self.get_object()
            history = obj.history.all()[:10].values()

            return Response(history, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({'data': str(ex)}, status=status.HTTP_400_BAD_REQUEST)



class KnoweldgebaseArticleSerializer(serializers.ModelSerializer):
    author_name = serializers.StringRelatedField(source="author.get_full_name", read_only=True)
    tags = serializers.StringRelatedField(many=True, read_only=True)
    category_name = serializers.StringRelatedField(source="category", read_only=True)

    class Meta:
        model = Article
        exclude = ("changed_by",)

class KnoweldgebaseArticleViewSet(viewsets.ModelViewSet):
    """
        Queryset
            Customers: status is True
            Staff: all
        Permissions:
            DjangoModelPermissions
            StaffRW_UserR_Permission
    """
    queryset = Article.objects.all()
    serializer_class = KnoweldgebaseArticleSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter,)
    permission_classes = (DjangoModelPermissions, StaffRW_UserR_Permission,)
    filter_fields = ('category', 'tags', 'author', 'created')
    order_fields = ('views', 'created', 'modified', 'author',)

    def get_queryset(self):
        filter = {}
        queryset = Article.objects.all()

        start_date = self.request.QUERY_PARAMS.get('start_date', None)
        end_date = self.request.QUERY_PARAMS.get('end_date', None)

        if start_date is not None:
            filter['created__gte'] = parser.parse(start_date)

        if end_date is not None:
            filter['created__lte'] = parser.parse(end_date)

        if not self.request.user.is_staff:
            filter['status'] = True

        queryset = queryset.filter(**filter)

        return queryset


    def perform_create(self, serializer):
        obj = serializer.save(author=self.request.user)
        action.send(self.request.user, verb='created', target=obj)

    def perform_update(self, serializer):
        obj = serializer.save()
        action.send(self.request.user, verb='modified', target=obj)

    def perform_delete(self, serializer):
        obj = serializer.save()
        action.send(self.request.user, verb='deleted', target=obj)

    @detail_route(methods=['get'])
    def history(self, request, pk):
        try:
            obj = self.get_object()
            history = obj.history.all()[:10].values()

            return Response(history, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({'data': str(ex)}, status=status.HTTP_400_BAD_REQUEST)

router = routers.DefaultRouter()
router.register('knowledgebase/articles', KnoweldgebaseArticleViewSet)
router.register('knowledgebase/categories', KnoweldgebaseCategoryViewSet)
router.register('knowledgebase/tags', KnoweldgebaseTagViewSet)
router.register('support/queues', QueueViewSet)
router.register('support/tickets', TicketViewSet)
router.register('support/posts', PostViewSet)
router.register('support/macros', MacroViewSet)
router.register('announcements', AnnouncementViewSet)
router.register('companies', CompanyViewSet)
router.register('contacts', ContactViewSet)
router.register('groups', GroupViewSet)
router.register('actions', ActionViewSet)