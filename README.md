# Timely

During the session, we had to work in many teams at the same time. We had to have meetings with everyone. It took a lot of time to coordinate the time. This inspired us to develop our project - an application that makes it easier to make appointments. In addition, the idea itself is not complicated and will allow to get acquainted with microservice architecture and set up all the necessary services and databases without going into project details. Our goal is to develop a simple appointment booking application to demonstrate how microservices work.

### Architecture:


![Untitled Diagram](https://github.com/user-attachments/assets/b3b475c2-1600-4fcd-8fcc-6ee05bc354d8)

### Use cases:
#### UC1: User Registration
- **Trigger:** User opens registration page  
- **Basic Flow:**  
  1. UI → auth-service: submit signup form  
  2. auth-service → DB: create new user record
  3. auth-service → mail-sender: send email verification
  4. auth-service → UI: show success or error  

#### UC2: User Login
- **Trigger:** User clicks “Login”  
- **Precondition:** User has valid credentials
- **Basic Flow:**  
  1. UI → auth-service: send credentials  
  2. auth-service → DB: verify credentials  
  3. auth-service → mail-sender: send email verification  
  4. auth-service → UI: return JWT or error  

#### UC3: View Available Slots
- **Trigger:** User navigates to “My Slots”  
- **Precondition:** Valid session token  
- **Basic Flow:**  
  1. UI → slots-service: request slot list  
  2. slots-service → DB: fetch free slots  
  3. slots-service → UI: return slot data

#### UC4: Add a slot
- **Trigger:** User navigates to “My Slots”  
- **Precondition:** Valid session token  
- **Basic Flow:**  
  1. UI → slots-service: slot post  
  2. slots-service → DB: add new slot
  3. slots-service → UI: return status  

#### UC5: Book Appointment
- **Trigger:** User selects slot and clicks “Book”  
- **Precondition:** Slot is still free
- **Basic Flow:**  
  1. UI → slots-service: submit booking request  
  2. slots-service → DB: reserve slot, create appointment record  
  4. slots-service → UI: show confirmation  
