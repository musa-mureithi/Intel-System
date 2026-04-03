import os
from django.conf import settings
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken
import json
from django.contrib.auth import get_user_model
User = get_user_model()
from .models import Operation, Report, Person, OperationAssignment
from .security import FIELD_CLEARANCE
from deepface import DeepFace
from .services.faiss_service import search_face
import pyotp
import qrcode
import io
import base64
from audit.security import detect_failed_logins
from audit.models import AuditLog
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404
from .utils.encryption import decrypt_data as decrypt




def home(request):
    return JsonResponse({
        "message": "Welcome to the CIA Agency API"
    })

@csrf_exempt
def login_view(request):
    if request.method != "POST":
        return JsonResponse({"message": "Send POST with credentials"}, status=405)

    try:
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")
        ip = request.META.get("REMOTE_ADDR")
        otp_code = data.get("otp_code")

        user = authenticate(username=username, password=password)
        if not user:
            AuditLog.objects.create(
            user=None,  
            ip_address=ip,
            action_type="FAILED_LOGIN"
              )
            danger_alert = detect_failed_logins()
            return JsonResponse({"message": "Unauthorized Login ", "danger_alert": danger_alert}, status=401)
        try:
            person = Person.objects.get(user=user)
        except Person.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Person not found"}, status=404)

        # Setup 2FA if missing
        if not person.totp_secret:
            person.totp_secret = pyotp.random_base32()
            person.save()

            totp_uri = pyotp.TOTP(person.totp_secret).provisioning_uri(
                name=username, issuer_name="CIA System"
            )
            qr_img = qrcode.make(totp_uri)
            buf = io.BytesIO()
            qr_img.save(buf, format="PNG")
            qr_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

            return JsonResponse({
                "status": "setup_2fa",
                "message": "Scan QR code with Google Authenticator",
                "qr_code": qr_b64
            })

        # Require OTP verification
        if not otp_code:
            return JsonResponse({"status": "require_otp", "message": "Enter your OTP code"})

        totp = pyotp.TOTP(person.totp_secret)
        if not totp.verify(otp_code):
            return JsonResponse({"status": "error", "message": "Invalid OTP"}, status=401)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        profile_data = {
            "full_name": person.full_name,
            "person_type": person.person_type,
            "unit_type": person.unit_type,
            "blood_type": person.blood_type,
            "id_dna": person.id_dna,
            "identity_number": person.identity_number,
            "status": person.status,
            "clearance_type": person.clearance_type,
            "totp_secret": person.totp_secret,
            "image": str(person.image) if person.image else None,
            "created_at": str(person.created_at),
        }

        return JsonResponse({
            "status": "success",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "profile": profile_data
        })

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    Logs out the user by blacklisting the refresh token.
    Access token will expire naturally, user cannot get new tokens.
    """
    try:
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"status": "error", "message": "Refresh token required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        token = RefreshToken(refresh_token)
        token.blacklist()  # mark the token as invalid

        return Response(
            {"status": "success", "message": "Logged out successfully"},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {"status": "error", "message": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


def process_assigned_personnel(input_text):
    """
    Takes comma-separated names.
    Returns:
      - matched_people: list of Person objects
      - unmatched_text: string of unmatched names
    """
    names = [name.strip() for name in input_text.split(",") if name.strip()]
    matched_people = []
    unmatched_names = []

    for name in names:
        try:
            person = Person.objects.get(full_name__iexact=name)
            matched_people.append(person)
        except Person.DoesNotExist:
            unmatched_names.append(name)

    unmatched_text = ", ".join(unmatched_names)
    return matched_people, unmatched_text


class OperationView(APIView):
    permission_classes = [IsAuthenticated]
    def _check_access(self, user, operation):
        profile = getattr(user, "person", None)
        if not profile:
            return False
        
        CLEARANCE_TYPE = {
            "UNCLASSIFIED": 0,
            "CONFIDENTIAL": 1,
            "CLASSIFIED": 2,
            "SECRET": 3,
            "TOP-SECRET": 4,
        }

        user_type = CLEARANCE_TYPE.get(profile.clearance_type.upper(), -1)
        op_type = CLEARANCE_TYPE.get(operation.clearance_type.upper(), -1)

        return user_type >= op_type
     # commander check only one allowed to create an Op
    def _is_high_rank(self, user):
        profile = getattr(user, "person", None)
        return profile and profile.clearance_level >= 4

    # GET all operations
    def get(self, request):
        profile = getattr(request.user, "person", None)
        if not profile:
            return Response({"status": "error", "message": "Access denied."}, status=403)
   # commander sees all ops, others see only those they are assigned to or have clearance for
        if self._is_high_rank(request.user):
            operations = Operation.objects.all()
        else:
            operations = [
                op for op in Operation.objects.all()
                if self._check_access(request.user, op)
            ]

        operations_list = []
        for op in operations:
            assigned_people = [
                {"id": a.person.id, "full_name": a.person.full_name, "person_type": a.person.person_type}
                for a in op.assignments.all()
        ]
            operations_list.append({
            "id": op.id,
            "identity_number": getattr(op, "identity_number", None),
            "mission_name": op.mission_name,
            "description": getattr(op, "description", None),
            "clearance_type": op.clearance_type,
            "Assigned_Personnel": assigned_people,
            "external_personnel": op.external_personnel.split(", ") if op.external_personnel else [],
            "created_by": {
                "full_name": op.created_by.full_name if op.created_by else None,
                "person_type": op.created_by.person_type if op.created_by else None
            },
            "updated_by": {
                "full_name": op.updated_by.full_name if op.updated_by else None,
                "person_type": op.updated_by.person_type if op.updated_by else None
            },
            "created_at": op.created_at,
            "updated_at": op.updated_at
            })

        return Response(operations_list, status=200)
    # POST create new operation
    def post(self, request):
        if not self._is_high_rank(request.user):
            return Response({"status": "error", "message": "Insufficient clearance."},
                            status=status.HTTP_403_FORBIDDEN)

        data = request.data
        required_fields = ["identity_number", "mission_name", "description", "clearance_type", "Assigned_Personnel"]
        if not all(data.get(f) for f in required_fields):
            return Response({"status": "error", "message": "All required fields must be provided."},
                            status=status.HTTP_400_BAD_REQUEST)

        profile = getattr(request.user, "person", None)
        operation = Operation.objects.create(
            identity_number=data["identity_number"],
            mission_name=data["mission_name"],
            description=data["description"],
            clearance_type=data["clearance_type"],
            created_by=profile,
        )

        # Process assigned personnel
        matched_people, unmatched_text = process_assigned_personnel(data["Assigned_Personnel"])
        for person in matched_people:
            OperationAssignment.objects.create(operation=operation, person=person)

        operation.external_personnel = unmatched_text
        operation.save()

        return Response({"status": "success", "message": "Operation created successfully", "operation_id": operation.id},
                        status=status.HTTP_201_CREATED)

    # PUT update operation
    def put(self, request, pk=None):
        if not self._is_high_rank(request.user):
            return Response({"status": "error", "message": "Insufficient clearance."},
                            status=status.HTTP_403_FORBIDDEN)
        if not pk:
            return Response({"status": "error", "message": "Operation ID required."}, status=status.HTTP_400_BAD_REQUEST)

        operation = get_object_or_404(Operation, pk=pk)
        data = request.data
        profile = getattr(request.user, "person", None)

        for field in ["identity_number", "mission_name", "description", "clearance_type"]:
            if field in data:
                setattr(operation, field, data[field])
        operation.updated_by = profile
        operation.save()

        if "Assigned_Personnel" in data:
            operation.assignments.all().delete()
            matched_people, unmatched_text = process_assigned_personnel(data["Assigned_Personnel"])
            for person in matched_people:
                OperationAssignment.objects.create(operation=operation, person=person)
            operation.external_personnel = unmatched_text
            operation.save()

        return Response({"status": "success", "message": "Operation updated successfully"}, status=status.HTTP_200_OK)


@permission_classes([IsAuthenticated])
def search_person(request):
    query = request.GET.get("q", "")
    if not query:
        return JsonResponse([], safe=False)
   
    try:
        user_clearance = int(request.user.person.clearance_level)
    except:
        user_clearance = 3   

    persons = Person.objects.filter(full_name__icontains=query)
    results = []

    for person in persons:
        filtered_data = {}

        
        if FIELD_CLEARANCE:
            for field, level in FIELD_CLEARANCE.items():
                if user_clearance >= level:
                    filtered_data[field] = getattr(person, field, None)

       
        filtered_data["id"] = person.id
        filtered_data["full_name"] = person.full_name
        #filtered_data["person_type"] = person.person_type
        #filtered_data["clearance_type"] = person.clearance_type
        #filtered_data["image"] = f"/media/{person.image}" if person.image else None

        results.append(filtered_data)

    return JsonResponse(results, safe=False)


HIGH_CLEARANCE_ROLES = ["DIRECTOR", "VCE-DIRECTOR", "COMMANDER"]

def can_view_report(user, report):
    if not user.is_authenticated:
        return False

    person = getattr(user, "person", None)
    if not person:
        return False

    if person.person_type in HIGH_CLEARANCE_ROLES:
        return True

    clearance_types = ["UNCLASSIFIED", "CONFIDENTIAL", "C" "SECRET", "TOP-SECRET"]
    try:
        user_type = clearance_types.index(person.clearance_type)
        report_level = clearance_types.index(report.role_based_access)
        return user_type >= report_level
    except ValueError:
        return False
    
HIGH_CLEARANCE = ["DIRECTOR", "VCE-DIRECTOR", "COMMANDER", "INTELLIGENCE-ANALYST"]

def has_high_clearance(user):
    person = getattr(user, "person", None)
    return bool(person and person.person_type in HIGH_CLEARANCE)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_report(request):
    if not has_high_clearance(request.user):
        return Response(
            {"message": "Access denied: insufficient clearance"},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        operation_id = request.data.get("operation_id")
        content = request.data.get("content")
        subject = request.data.get("subject")
        role_based_access = request.data.get("role_based_access")

        operation = get_object_or_404(Operation, id=operation_id)
        person = request.user.person

        report = Report.objects.create(
            operation_id=operation.id,
            operation=operation,
            author=person,
            content=content,
            subject=subject,
            role_based_access=role_based_access
            
        ) 

        return Response({
            "status": "success",
            "message": "Report created",
            "report_id": report.id
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        print("ERROR:", str(e))
        return Response(
            {"status": "error", "message": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

    
@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def report_detail(request, report_id):
    report = get_object_or_404(Report, id=report_id)

    if not has_high_clearance(request.user):
        return Response(
            {"message": "Access denied: insufficient clearance"},
            status=status.HTTP_403_FORBIDDEN
        )

   
    if request.method == "GET":
        data = {
            "id": report.id,
            "operation": report.operation.mission_name,
            "subject": report.subject,
            "content": report.content,
            "author": report.author.full_name if report.author else None,
            "role_based_access": report.role_based_access,
            "created_at": report.created_at,
        }
        return Response({"status": "success", "report": data})

  
    if request.method in ["PUT", "PATCH"]:
        report.subject = request.data.get("subject", report.subject)
        report.content = request.data.get("content", report.content)
        report.role_based_access = request.data.get("role_based_access", report.role_based_access)
        report.save()
        return Response({"status": "success", "message": "Report updated"})

   
    if request.method == "DELETE":
        report.delete()
        return Response({"status": "success", "message": "Report deleted"})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_reports(request):
    try:
        all_reports = Report.objects.all()
        accessible_reports = [
            r for r in all_reports if can_view_report(request.user, r)
        ]

        result = [{
            "id": r.id,
            "operation": r.operation.mission_name,
            "subject": r.subject,
            "author": r.author.full_name if r.author else None,
            "content": r.content,
            "role_based_access": r.role_based_access,
            "created_at": r.created_at
        } for r in accessible_reports]

        return Response({
            "status": "success",
            "reports": result
        })

    except Exception as e:
        print("ERROR:", str(e))
        return Response(
            {"status": "error", "message": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unified_search(request):
    """
    Unified search endpoint.
    Search by image, identity_number, or DNA ID.
    """
    image_file = request.FILES.get("image_file")
    identity_number = request.data.get("identity_number", "").strip()
    dna_id = request.data.get("dna_id", "").strip()

    try:
        
        if image_file:
            temp_path = os.path.join(settings.BASE_DIR, "temp_upload.jpg")
            # Save uploaded image temporarily
            with open(temp_path, "wb") as f:
                for chunk in image_file.chunks():
                    f.write(chunk)

            
            result = DeepFace.represent(
                img_path=temp_path,
                enforce_detection=True
            )

           
            os.remove(temp_path)

            if not result or len(result) == 0:
                return Response({"message": "Face embedding extraction failed"}, status=400)

            upload_embedding = result[0]['embedding']
            

           
            person, distance = search_face(upload_embedding)
            if not person:
                return Response({"message": "No match found"}, status=404)

            return _build_response(request, person, distance)

        
        if identity_number or dna_id:
            persons = Person.objects.all()
            matched_person = None

            for person in persons:
                decrypted_dna = decrypt(person.id_dna) if person.id_dna else None

                identity_match = identity_number and person.identity_number == identity_number
                dna_match = dna_id and decrypted_dna == dna_id

                if identity_match or dna_match:
                    matched_person = person
                    break

            if not matched_person:
                return Response({"message": "Person not found"}, status=404)

            return _build_response(request, matched_person)

        
        return Response(
            {"error": "Provide image OR identity_number OR dna_id"},
            status=status.HTTP_400_BAD_REQUEST
        )

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



def _build_response(request, person, distance=None):
    """
    Build JSON response for a person, respecting clearance levels.
    """
    try:
        user_clearance = int(request.user.person.clearance_level)
    except AttributeError:
        user_clearance = 3 

    if user_clearance < person.clearance_level:
        return Response({"message": "MATCH FOUND - CLASSIFIED"}, status=403)

    image_url = person.image.url if person.image and hasattr(person.image, 'url') else None

    return Response({
        "id": person.id,
        "full_name": person.full_name,
        "person_type": getattr(person, "person_type", None),
        "status": getattr(person, "status", None),
        "blood_type": getattr(person, "blood_type", None),
        "id_dna": decrypt(person.id_dna) if person.id_dna else None,
        "image": image_url,
        "unit_type": getattr(person, "unit_type", None),
        "OperationAssignment": [getattr(getattr(a, "operation", None), "mission_name", None) for a in person.assignments.all()],
        "match_confidence": float(distance) if distance is not None else None
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard(request):

    try:
        person = Person.objects.get(user=request.user)
        image_url = person.image.url if person.image and hasattr(person.image, 'url') else None

        profile_data = {
            "full_name": person.full_name,
            "person_type": person.person_type,
            "unit_type": person.unit_type,
            "blood_type": person.blood_type,
            "id_dna": person.id_dna,
            "identity_number": person.identity_number,
            "status": person.status,
            "clearance_type": person.clearance_type,
            "totp_secret": person.totp_secret,
            "image":image_url,
            "created_at": str(person.created_at),
           # "Operation": str(person.Operation)
        }
        
        return Response({"profile": profile_data})
    except Person.DoesNotExist:
        return Response({"error": "Person not found"}, status=404)
    
    