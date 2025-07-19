from neomodel import StructuredNode, StringProperty,BooleanProperty,IntegerProperty,UniqueIdProperty, RelationshipTo, RelationshipFrom,DateProperty,DateTimeProperty,ArrayProperty, StructuredRel
from django.conf import settings
from datetime import datetime
from django.db import models
from uuid import uuid4
import base64

class WebAuthnCredential(StructuredNode):
    """Store WebAuthn credentials for Face ID/Touch ID authentication"""
    uid = StringProperty()  # User ID this credential belongs to
    credential_id = StringProperty(unique_index=True, required=True)  # Base64 encoded credential ID
    public_key = StringProperty(required=True)  # Base64 encoded public key
    sign_count = IntegerProperty(default=0)  # Signature counter
    credential_type = StringProperty(default="public-key")  # Always "public-key" for WebAuthn
    transports = ArrayProperty(StringProperty())  # Transport methods (internal, etc.)
    created_at = DateTimeProperty(default_now=True)
    last_used = DateTimeProperty(default_now=True)
    is_active = BooleanProperty(default=True)
    
    # Additional metadata
    aaguid = StringProperty(default="")  # Authenticator Attestation GUID
    device_name = StringProperty(default="")  # User-friendly device name
    
    def update_last_used(self):
        """Update the last used timestamp"""
        self.last_used = datetime.now()
        self.save()

class Signups(StructuredNode):
    uid = StringProperty()
    username = StringProperty(required=True)
    email = StringProperty(unique_index=True, required=True)
    password = StringProperty(required=True)
    dob = DateProperty()
    gender = StringProperty(required=True)
    face_id = BooleanProperty(default=False)
    profile_image = StringProperty()
    ip = StringProperty(default=None,blank=True)
    
    # WebAuthn support
    webauthn_enabled = BooleanProperty(default=False)
    challenge = StringProperty()  # Temporary challenge for WebAuthn operations

    chat = RelationshipTo('History_Chat', 'HAS')
    sense = RelationshipTo('SensoryMemory', 'SENSES')
    webauthn_credentials = RelationshipTo('WebAuthnCredential', 'HAS_CREDENTIAL')

    class Meta:
        labels = ["Signups","Person"]


class History_Chat(StructuredNode):
    uid = StringProperty()
    name = StringProperty()
    chat = ArrayProperty(StringProperty())
    created_at = DateTimeProperty(default_now=True)
    memory_list = ArrayProperty(StringProperty())

    history = RelationshipTo('Session_History', 'HAS')

class Episode_Part(StructuredNode):
    uid = StringProperty()
    name = StringProperty()
    response = StringProperty()
    sentiments = StringProperty(default=None,blank=True)
    created_at = StringProperty(default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    relation = RelationshipFrom('Session_History', 'HAS_CHAT')

class Session_History(StructuredNode):
    uid = StringProperty()
    name = StringProperty()
    start_session = DateTimeProperty(default_now=True)
    overall_sentiments = StringProperty(default='neutral')
    memory_list = ArrayProperty(StringProperty())

    def save_message(self, message_type, message_content):
        if self.memory_list is None:
            self.memory_list = []

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"{timestamp} - {message_type}: {message_content}"
        self.memory_list.append(formatted_message)
        self.save()

class Person(StructuredNode):
    uid = StringProperty(blank=True)
    full_name = StringProperty(blank=True)
    created_at = StringProperty(default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    parent = RelationshipTo('Person','IS_PARENT_OF')
    fact  = RelationshipTo('Attribute','IS')

class Attribute(StructuredNode):
    uid = StringProperty(blank=True)
    attribute = StringProperty(blank=True)
    created_at = StringProperty(default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


class SocialNetwork(StructuredNode):
    uid = StringProperty(unique_index=True)
    name = StringProperty()
    gender = StringProperty()
    created_at = StringProperty(default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.uid = str(uuid4())

class SensoryMemory(StructuredNode):
    uid = StringProperty(unique_index=True)
    name = StringProperty()
    created_at = StringProperty(default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S')) 

    textsense = RelationshipTo('TextSensor', 'HAS_SENTENCE')
    sensor = RelationshipTo('Sensor', 'HAS_SENSOR')

class TextSensor(StructuredNode):
    uid = StringProperty(unique_index=True)
    name = StringProperty()
    created_at = StringProperty(default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    text_sense = RelationshipTo('CommandText', 'HAS')

class Sensor(StructuredNode):
    uid = StringProperty()
    name = StringProperty()
    created_at = StringProperty(default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    sense = RelationshipTo('Sense', 'SENSES')

class CommandText(StructuredNode):
    # uid = StringProperty()
    sentence = StringProperty()
    created_at = StringProperty(default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    text_part = RelationshipTo('CommandPart', 'HAS_PART')


class CommandPart(StructuredNode):
    # uid = StringProperty()
    part = StringProperty()
    created_at = StringProperty(default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))   


class Sense(StructuredNode):
    # uid = StringProperty(unique_index=False)
    sense_name = StringProperty(default="FLIGHT")
    temperature_range = StringProperty()
    lowest_temperature = StringProperty()
    highest_temperature = StringProperty()
    battery = StringProperty()
    barometer = StringProperty()
    attitude = StringProperty()
    speed = StringProperty()
    height = StringProperty()
    flight_time = StringProperty()
    distance_tof = StringProperty()
    updated_on = StringProperty(default='None')
    created_at = StringProperty(default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

# =================================================================================================

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    message = models.TextField()

    def __str__(self):
        return self.email

class FAQS(models.Model):
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "FAQ"

    def __str__(self):
        return self.question