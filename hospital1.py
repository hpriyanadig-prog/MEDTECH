from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime


# ============================================================
# ENUMS
# ============================================================

class ResourceStatus(Enum):
    AVAILABLE = "available"
    ALLOCATED = "allocated"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    UNAVAILABLE = "unavailable"


class PatientCondition(Enum):
    STABLE = "stable"
    SERIOUS = "serious"
    CRITICAL = "critical"
    DECEASED = "deceased"


class PatientLocation(Enum):
    EMERGENCY = "emergency"
    ICU = "icu"
    WARD = "ward"
    OPERATING_THEATRE = "operating_theatre"
    DISCHARGED = "discharged"


class BloodGroup(Enum):
    A_POS = "A+"
    A_NEG = "A-"
    B_POS = "B+"
    B_NEG = "B-"
    AB_POS = "AB+"
    AB_NEG = "AB-"
    O_POS = "O+"
    O_NEG = "O-"


# ============================================================
# BASE RESOURCE
# ============================================================

@dataclass
class Resource:
    resource_id: str
    name: str
    status: ResourceStatus = ResourceStatus.AVAILABLE


# ============================================================
# HUMAN RESOURCES
# ============================================================

@dataclass
class MedicalStaff(Resource):
    employee_id: str = ""
    specialization: Optional[str] = None
    shift: Optional[str] = None


@dataclass
class Doctor(MedicalStaff):
    pass


@dataclass
class Surgeon(Doctor):
    surgical_specialization: Optional[str] = None


@dataclass
class Nurse(MedicalStaff):
    nursing_level: Optional[str] = None


@dataclass
class Technician(MedicalStaff):
    technical_specialization: Optional[str] = None


@dataclass
class SupportStaff(MedicalStaff):
    role: Optional[str] = None


# ============================================================
# PHYSICAL HOSPITAL RESOURCES
# ============================================================

@dataclass
class Bed(Resource):
    ward_name: Optional[str] = None
    patient_id: Optional[str] = None


@dataclass
class NormalBed(Bed):
    pass


@dataclass
class ICUBed(Bed):
    isolation_capable: bool = False


@dataclass
class SpecialWardBed(Bed):
    ward_type: Optional[str] = None


@dataclass
class OperatingTheatre(Resource):
    theatre_number: str = ""
    speciality: Optional[str] = None


@dataclass
class MedicalEquipment(Resource):
    equipment_type: str = ""
    location: Optional[str] = None


@dataclass
class Ventilator(MedicalEquipment):
    model: Optional[str] = None


@dataclass
class PatientMonitor(MedicalEquipment):
    monitor_type: Optional[str] = None


@dataclass
class ImagingEquipment(MedicalEquipment):
    modality: Optional[str] = None


# ============================================================
# EXTERNAL / CONSUMABLE RESOURCES
# ============================================================

@dataclass
class ExternalResource:
    resource_id: str
    name: str
    quantity: float
    unit: str
    available: bool = True


@dataclass
class Blood(ExternalResource):
    blood_group: Optional[BloodGroup] = None


@dataclass
class OxygenCylinder(ExternalResource):
    capacity_litres: Optional[float] = None
    pressure_bar: Optional[float] = None


@dataclass
class Medicine(ExternalResource):
    medicine_name: str = ""
    dosage: Optional[str] = None


@dataclass
class MedicalConsumable(ExternalResource):
    category: Optional[str] = None


# ============================================================
# PATIENT
# ============================================================

@dataclass
class Patient:
    patient_id: str
    name: str
    age: int
    condition: PatientCondition = PatientCondition.STABLE
    location: PatientLocation = PatientLocation.EMERGENCY

    blood_group: Optional[BloodGroup] = None

    assigned_doctor: Optional[str] = None
    assigned_surgeon: Optional[str] = None
    assigned_nurse: Optional[str] = None

    assigned_bed: Optional[str] = None
    assigned_ventilator: Optional[str] = None

    required_oxygen: bool = False
    surgery_required: bool = False

    notes: List[str] = field(default_factory=list)
    arrival_time: datetime = field(default_factory=datetime.now)
    emergency_level: int = 1


# ============================================================
# HOSPITAL
# ============================================================

@dataclass
class Hospital:
    hospital_id: str
    name: str

    doctors: List[Doctor] = field(default_factory=list)
    surgeons: List[Surgeon] = field(default_factory=list)
    nurses: List[Nurse] = field(default_factory=list)
    technicians: List[Technician] = field(default_factory=list)
    support_staff: List[SupportStaff] = field(default_factory=list)

    beds: List[Bed] = field(default_factory=list)
    operating_theatres: List[OperatingTheatre] = field(default_factory=list)
    equipment: List[MedicalEquipment] = field(default_factory=list)

    external_resources: List[ExternalResource] = field(default_factory=list)
    patients: List[Patient] = field(default_factory=list)
    waiting_patients: List[Patient] = field(default_factory=list)
    def patient_management_loop(self):

        while True:

            print("\n================================")
            print("       PATIENT MANAGEMENT")
            print("================================")

            print("\n1. Register new patient")
            print("2. Discharge patient")
            print("3. Show hospital status")
            print("4. Exit")

            choice = input("\nEnter your choice: ")

        # ------------------------------------------
        # NEW PATIENT
        # ------------------------------------------

            if choice == "1":

                patient_id = input("Enter patient ID: ")
                name = input("Enter patient name: ")
                age = int(input("Enter patient age: "))

                print("\nCondition:")
                print("1. Stable")
                print("2. Serious")
                print("3. Critical")

                condition_choice = input("Enter choice: ")

                if condition_choice == "1":
                    condition = PatientCondition.STABLE

                elif condition_choice == "2":
                    condition = PatientCondition.SERIOUS

                elif condition_choice == "3":
                    condition = PatientCondition.CRITICAL

                else:
                    print("Invalid condition.")
                    continue

            # Create patient
                patient = Patient(
                    patient_id=patient_id,
                    name=name,
                    age=age,
                    condition=condition
                )

            # Register patient
                self.register_patient(patient)
                # Add patient to priority queue
                self.add_to_waiting_queue(patient)

                # Process waiting queue
                self.process_waiting_queue()

                self.show_status()

        # ------------------------------------------
        # DISCHARGE PATIENT
        # ------------------------------------------

            elif choice == "2":

                patient_id = input("Enter patient ID to discharge: ")

                patient = self.get_patient(patient_id)

                if patient is None:

                    print("Patient not found.")
                    continue

            # Release doctor
                if patient.assigned_doctor is not None:

                    for doctor in self.doctors:

                        if doctor.resource_id == patient.assigned_doctor:

                            doctor.status = ResourceStatus.AVAILABLE

                            print(f"Doctor {doctor.name} is now available.")
                            break

            # Release bed
                if patient.assigned_bed is not None:

                    for bed in self.beds:

                        if bed.resource_id == patient.assigned_bed:

                            bed.status = ResourceStatus.AVAILABLE
                            bed.patient_id = None

                            print(f"Bed {bed.name} is now available.")
                            break

            # Release ventilator
                if patient.assigned_ventilator is not None:

                    for equipment in self.equipment:

                        if equipment.resource_id== patient.assigned_ventilator:

                            equipment.status = ResourceStatus.AVAILABLE

                            print(
                                f"Ventilator {equipment.name} "
                                f"is now available."
                            )

                            break

                patient.location = PatientLocation.DISCHARGED

                print(
                    f"Patient {patient.name} discharged successfully."
                )
                self.process_waiting_queue()
                self.show_status()

        # ------------------------------------------
        # SHOW STATUS
        # ------------------------------------------

            elif choice == "3":

                self.show_status()

        # ------------------------------------------
        # EXIT
        # ------------------------------------------

            elif choice == "4":

                print("Exiting patient management system.")
                break

            else:

                print("Invalid choice. Please try again.")

    # ========================================================
    # 1. ADD RESOURCES
    # ========================================================

    def add_doctor(self, doctor):
        self.doctors.append(doctor)
        print(f"Doctor {doctor.name} added successfully.")

    def add_surgeon(self, surgeon):
        self.surgeons.append(surgeon)
        print(f"Surgeon {surgeon.name} added successfully.")

    def add_nurse(self, nurse):
        self.nurses.append(nurse)
        print(f"Nurse {nurse.name} added successfully.")

    def add_bed(self, bed):
        self.beds.append(bed)
        print(f"Bed {bed.name} added successfully.")

    def add_equipment(self, equipment):
        self.equipment.append(equipment)
        print(f"Equipment {equipment.name} added successfully.")

    def add_external_resource(self, resource):
        self.external_resources.append(resource)
        print(f"Resource {resource.name} added successfully.")


    # ========================================================
    # 2. REGISTER PATIENT
    # ========================================================

    def register_patient(self, patient):

        self.patients.append(patient)

        print(
            f"Patient {patient.patient_id} "
            f"({patient.name}) registered successfully."
        )


    # ========================================================
    # 3. GET PATIENT
    # ========================================================

    def get_patient(self, patient_id):

        for patient in self.patients:

            if patient.patient_id == patient_id:
                return patient

        return None
    def calculate_priority(self, patient):

        if patient.condition == PatientCondition.CRITICAL:
            emergency_priority = 3

        elif patient.condition == PatientCondition.SERIOUS:
            emergency_priority = 2

        else:
            emergency_priority = 1

        waiting_time = (
            datetime.now() - patient.arrival_time
        ).total_seconds()

        priority_score = (
            emergency_priority * 100000
            + waiting_time
        )

        return priority_score
    def add_to_waiting_queue(self, patient):

        if patient not in self.waiting_patients:

            self.waiting_patients.append(patient)

            print(
                f"Patient {patient.name} added "
                f"to the waiting queue."
            )
    def get_next_patient(self):

        if not self.waiting_patients:
            return None

        highest_priority_patient = max(
            self.waiting_patients,
            key=self.calculate_priority
        )

        return highest_priority_patient
        # ========================================================
    # 6. PROCESS WAITING QUEUE
    # ========================================================

    def process_waiting_queue(self):

        while self.waiting_patients:

            patient = self.get_next_patient()

            if patient is None:
                return

            print(
                f"\nProcessing patient: {patient.name}"
            )

            # Find doctor
            doctor = self.find_available_doctor()

            if doctor is None:
                print("No doctor available.")
                return

            # Find suitable bed
            if patient.condition == PatientCondition.CRITICAL:
                bed = self.find_available_bed(ICUBed)
            else:
                bed = self.find_available_bed(NormalBed)

            if bed is None:
                print("No suitable bed available.")
                return

            # Allocate doctor
            doctor.status = ResourceStatus.ALLOCATED
            patient.assigned_doctor = doctor.resource_id

            # Allocate bed
            bed.status = ResourceStatus.ALLOCATED
            bed.patient_id = patient.patient_id
            patient.assigned_bed = bed.resource_id

            print(
                f"Doctor {doctor.name} assigned."
            )

            print(
                f"Bed {bed.name} assigned."
            )

            # Critical patient gets ventilator
            if patient.condition == PatientCondition.CRITICAL:

                for equipment in self.equipment:

                    if isinstance(equipment, Ventilator):

                        if equipment.status == ResourceStatus.AVAILABLE:

                            equipment.status = ResourceStatus.ALLOCATED

                            patient.assigned_ventilator = (
                                equipment.resource_id
                            )

                            print(
                                f"Ventilator "
                                f"{equipment.name} assigned."
                            )

                            break

            # Remove patient from waiting queue
            self.waiting_patients.remove(patient)

            print(
                f"Patient {patient.name} "
                f"is now receiving treatment."
            )
        


    # ========================================================
    # 4. FIND AVAILABLE DOCTOR
    # ========================================================

    def find_available_doctor(self, specialization=None):

        for doctor in self.doctors:

            if doctor.status != ResourceStatus.AVAILABLE:
                continue

            if specialization is not None:

                if doctor.specialization != specialization:
                    continue

            return doctor

        return None


    # ========================================================
    # 5. ASSIGN DOCTOR
    # ========================================================

    def assign_doctor(self, patient_id, specialization=None):

        patient = self.get_patient(patient_id)

        if patient is None:

            print("Patient not found.")
            return False

        doctor = self.find_available_doctor(specialization)

        if doctor is None:

            print("No doctor available.")
            return False

        doctor.status = ResourceStatus.ALLOCATED

        patient.assigned_doctor = doctor.resource_id

        print(
            f"Doctor {doctor.name} assigned to "
            f"patient {patient.name}."
        )

        return True


    # ========================================================
    # 6. FIND AVAILABLE BED
    # ========================================================

    def find_available_bed(self, bed_type):

        for bed in self.beds:

            if bed.status != ResourceStatus.AVAILABLE:
                continue

            if isinstance(bed, bed_type):
                return bed

        return None


    # ========================================================
    # 7. ASSIGN BED
    # ========================================================

    def assign_bed(self, patient_id, bed_type):

        patient = self.get_patient(patient_id)

        if patient is None:

            print("Patient not found.")
            return False

        bed = self.find_available_bed(bed_type)

        if bed is None:

            print("No suitable bed available.")
            return False

        bed.status = ResourceStatus.ALLOCATED

        bed.patient_id = patient.patient_id

        patient.assigned_bed = bed.resource_id

        print(
            f"Bed {bed.resource_id} assigned to "
            f"patient {patient.name}."
        )

        return True


    # ========================================================
    # 8. ASSIGN VENTILATOR
    # ========================================================

    def assign_ventilator(self, patient_id):

        patient = self.get_patient(patient_id)

        if patient is None:

            print("Patient not found.")
            return False

        for equipment in self.equipment:

            if not isinstance(equipment, Ventilator):
                continue

            if equipment.status != ResourceStatus.AVAILABLE:
                continue

            equipment.status = ResourceStatus.ALLOCATED

            patient.assigned_ventilator = equipment.resource_id

            print(
                f"Ventilator {equipment.resource_id} "
                f"assigned to patient {patient.name}."
            )

            return True

        print("No ventilator available.")
        return False


    # ========================================================
    # 9. RESOURCE COUNTS
    # ========================================================

    def count_available_beds(self):

        count = 0

        for bed in self.beds:

            if bed.status == ResourceStatus.AVAILABLE:
                count += 1

        return count


    def count_allocated_beds(self):

        count = 0

        for bed in self.beds:

            if bed.status == ResourceStatus.ALLOCATED:
                count += 1

        return count


    def count_available_doctors(self):

        count = 0

        for doctor in self.doctors:

            if doctor.status == ResourceStatus.AVAILABLE:
                count += 1

        return count


    def count_available_ventilators(self):

        count = 0

        for equipment in self.equipment:

            if isinstance(equipment, Ventilator):

                if equipment.status == ResourceStatus.AVAILABLE:
                    count += 1

        return count


    # ========================================================
    # 10. SHOW HOSPITAL STATUS
    # ========================================================

    def show_status(self):

        print("\n")
        print("============================================")
        print("          HOSPITAL STATUS")
        print("============================================")

        print(f"Hospital: {self.name}")
        print(f"Total patients: {len(self.patients)}")

        print("\n--- BEDS ---")
        print(f"Total beds: {len(self.beds)}")
        print(f"Available beds: {self.count_available_beds()}")
        print(f"Allocated beds: {self.count_allocated_beds()}")

        print("\n--- STAFF ---")
        print(f"Total doctors: {len(self.doctors)}")
        print(f"Available doctors: {self.count_available_doctors()}")

        print("\n--- EQUIPMENT ---")
        print(
            f"Available ventilators: "
            f"{self.count_available_ventilators()}"
        )

        print("============================================")
        print()


# ============================================================
# CREATE HOSPITAL
# ============================================================

hospital = Hospital(
    hospital_id="H001",
    name="BMS Medical Emergency Hospital-- Bangalore",
)


# ============================================================
# CREATE DOCTORS
# ============================================================

hospital.add_doctor(
    Doctor(
        resource_id="DOC001",
        name="Dr. Ravi",
        employee_id="E001",
        specialization="Cardiology",
        shift="Day"
    )
)

hospital.add_doctor(
    Doctor(
        resource_id="DOC002",
        name="Dr. Mehta",
        employee_id="E002",
        specialization="Neurology",
        shift="Day"
    )
)


# ============================================================
# CREATE SURGEON
# ============================================================

hospital.add_surgeon(
    Surgeon(
        resource_id="SUR001",
        name="Dr. Kumar",
        employee_id="E003",
        specialization="General Surgery",
        surgical_specialization="Trauma Surgery",
        shift="Day"
    )
)

hospital.add_surgeon(
    Surgeon(
        resource_id="SUR002",
        name="Dr. Maesh",
        employee_id="E024",
        specialization="General Surgery",
        surgical_specialization="Cordioc Surgery",
        shift="Day"
    )
)
# ============================================================
# CREATE NURSE
# ============================================================

hospital.add_nurse(
    Nurse(
        resource_id="NUR001",
        name="Nurse Anita",
        employee_id="E101",
        nursing_level="ICU",
        shift="Night"
    )
)

hospital.add_nurse(
    Nurse(
        resource_id="NUR002",
        name="Nurse Veena",
        employee_id="E125",
        nursing_level="ICU",
        shift="Day"
    )
)

# ============================================================
# CREATE BEDS USING RANGE
# ============================================================

# 5 normal beds

for i in range(1, 6):

    hospital.add_bed(
        NormalBed(
            resource_id=f"BED-{i:03d}",
            name=f"Normal Bed {i}",
            ward_name="General Ward"
        )
    )


# 3 ICU beds

for i in range(1, 4):

    hospital.add_bed(
        ICUBed(
            resource_id=f"ICU-B{i:02d}",
            name=f"ICU Bed {i}",
            ward_name="ICU-1",
            isolation_capable=True
        )
    )


# 2 special ward beds

for i in range(1, 3):

    hospital.add_bed(
        SpecialWardBed(
            resource_id=f"SW-{i:02d}",
            name=f"Special Ward Bed {i}",
            ward_name="Special Ward",
            ward_type="Cardiac"
        )
    )


# ============================================================
# OPERATING THEATRE
# ============================================================

hospital.operating_theatres.append(
    OperatingTheatre(
        resource_id="OT001",
        name="Operating Theatre 1",
        theatre_number="OT-1",
        speciality="General Surgery"
    )
)


# ============================================================
# VENTILATORS USING RANGE
# ============================================================

for i in range(1, 4):

    hospital.add_equipment(
        Ventilator(
            resource_id=f"VENT{i:03d}",
            name=f"Ventilator {i}",
            equipment_type="Ventilator",
            location="ICU-1",
            model="Model-X"
        )
    )


# ============================================================
# BLOOD
# ============================================================

hospital.add_external_resource(
    Blood(
        resource_id="BLOOD001",
        name="O Positive Blood",
        quantity=10,
        unit="units",
        blood_group=BloodGroup.O_POS
    )
)


# ============================================================
# OXYGEN
# ============================================================

hospital.add_external_resource(
    OxygenCylinder(
        resource_id="OXY001",
        name="Oxygen Cylinder",
        quantity=20,
        unit="cylinders",
        capacity_litres=7000,
        pressure_bar=150
    )
)


# ============================================================
# INITIAL STATUS
# ============================================================
if __name__ == "__main__":
    print("\nINITIAL HOSPITAL STATUS")
    hospital.show_status()
    print("\nDeveloped by Haripriya,Krithika,Harika-BMSCE sem-1")
    hospital.patient_management_loop()




