# CS218 Assignment 2


## Deployment Info

EC2 Instance Type: t2.micro, Amazon Linux 2023

Public IP: 3.141.40.35

Port: 8080

Database: SQLite (orders.db)


### Security Group Inbound Rules

SSH, 22, 0.0.0.0/0

Custom TCP, 8080, 0.0.0.0/0


---

## Project Structure
```
README.md
db/
├── app.py          # Main Flask application
├── database.py     # SQLite connection and helpers
└── schema.sql      # Database table definitions
```

---

## Steps to Deploy and Run

### 1. SSH into EC2
```bash
ssh -i "your-key.pem" ec2-user@3.141.40.35
```

### 2. Install dependencies
```bash
sudo dnf install python3-pip git sqlite -y
```

### 3. Clone the repository
```bash
git clone https://github.com/Mingkun0906/CS218-Assignment2.git
cd CS218-Assignment2/db
```

### 4. Install Python packages
```bash
pip3 install flask
```

### 5. Run the server
```bash
nohup python3 app.py > app.log 2>&1 &
```

### 6. Verify the server is running
```bash
curl http://localhost:8080/orders/fake-id
# Expected: {"error": "Order not found"}
```

### 7. View logs
```bash
tail -f app.log
```

### 8. Stop the server
```bash
pkill -f "python3 app.py"
```

---

## Verification Steps

### Step 1 — Basic Order Creation
```bash
curl -X POST http://3.141.40.35:8080/orders \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: test-123" \
  -d '{"customer_id":"cust1","item_id":"item1","quantity":1}'
```

---

### Step 2 — Retry with Same Idempotency Key
```bash
curl -X POST http://3.141.40.35:8080/orders \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: test-123" \
  -d '{"customer_id":"cust1","item_id":"item1","quantity":1}'
```

---

### Step 3 — Same Key, Different Payload (Conflict Case)
```bash
curl -X POST http://3.141.40.35:8080/orders \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: test-123" \
  -d '{"customer_id":"cust1","item_id":"item1","quantity":5}'
```

---

### Step 4 — Simulated Failure After Commit
```bash
curl -X POST http://3.141.40.35:8080/orders \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: test-fail-1" \
  -H "X-Debug-Fail-After-Commit: true" \
  -d '{"customer_id":"cust2","item_id":"item2","quantity":1}'
```

---

### Step 5 — Retry After Simulated Failure
```bash
curl -X POST http://3.141.40.35:8080/orders \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: test-fail-1" \
  -d '{"customer_id":"cust2","item_id":"item2","quantity":1}'
```

---

### Step 6 — Verify Order Exists
Replace `<order_id>` with the `order_id` returned from Step 1:
```bash
curl http://3.141.40.35:8080/orders/<order_id>
```

---
