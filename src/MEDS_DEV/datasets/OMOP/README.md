# OMOP Dataset Predicates

This README provides an overview of predicates defined for the OMOP dataset to represent various healthcare events. Each predicate is defined with specific codes or patterns that are used to identify events, such as admissions, discharges, and other clinical encounters, within the OMOP format.

## Predicates Overview

### 1. **hospital_admission**

- **Codes**:
    - `Visit/IP`: Inpatient visit.
    - `Visit/ERIP`: Emergency room to inpatient visit.
    - `CMS Place of Service/51`: Inpatient Psychiatric Facility.
    - `CMS Place of Service/61`: Comprehensive Inpatient Rehabilitation Facility.

### 2. **hospital_discharge**

- **Codes**:
    - `CMS Place of Service/12`: Home.
    - `CMS Place of Service/31`: Skilled Nursing Facility.
    - `SNOMED/371827001`: Discharge to another healthcare facility.
    - `PCORNet/Generic-NI`: Noninstitutional (self-care).
    - `SNOMED/397709008`: Hospice care.
    - `Medicare Specialty/A4`: Hospice provider.
    - `CMS Place of Service/21`: Inpatient hospital.
    - `CMS Place of Service/61`: Comprehensive Inpatient Rehabilitation Facility.
    - `CMS Place of Service/51`: Inpatient Psychiatric Facility.
    - `SNOMED/225928004`: Transfer to intermediate care facility.
    - `CMS Place of Service/34`: Hospice.
    - `PCORNet/Generic-OT`: Other.
    - `CMS Place of Service/27`: Ambulatory Surgical Center.
    - `CMS Place of Service/33`: Custodial Care Facility.
    - `CMS Place of Service/09`: Prison/Correctional Facility.
    - `CMS Place of Service/32`: Nursing Facility.

### 3. **ED_registration**

- **Code**:
    - `Visit/ER`: Emergency room visit.

### 4. **ED_discharge**

- **Codes**:
    - `CMS Place of Service/12`: Home.
    - `PCORNet/Generic-NI`: Noninstitutional (self-care).
    - `SNOMED/371827001`: Discharge to other healthcare facility.
    - `CMS Place of Service/21`: Inpatient hospital.
    - `NUCC/261Q00000X`: Clinic/Center.
    - `SNOMED/225928004`: Transfer to intermediate care facility.
    - `CMS Place of Service/51`: Inpatient Psychiatric Facility.
    - `CMS Place of Service/23`: Emergency Room - Hospital.
    - `CMS Place of Service/31`: Skilled Nursing Facility.
    - `CMS Place of Service/34`: Hospice.
    - `SNOMED/397709008`: Hospice care.
    - `CMS Place of Service/24`: Ambulatory Surgical Center.
    - `SNOMED/34596002`: Discharge to home under care of a home health service.
    - `PCORNet/Generic-OT`: Other.
    - `CMS Place of Service/09`: Prison/Correctional Facility.

### 5. **death**

- **Code**:
    - `MEDS_DEATH`: Indicator of patient death.

## Usage

Each predicate is defined in the YAML file, allowing for flexible querying and filtering of the OMOP dataset. The structure leverages the codes and patterns specified under each predicate to capture relevant patient events.
