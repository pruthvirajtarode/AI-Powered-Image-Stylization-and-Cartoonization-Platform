# Use Case Diagram - Toonify AI

```mermaid
graph TB
    subgraph Users
        U1["👤 Free User"]
        U2["💳 Premium User"]
        U3["⚙️ Admin"]
    end
    
    subgraph System["🎨 Toonify AI System"]
        UC1["Upload Image"]
        UC2["Select Style"]
        UC3["Process Image"]
        UC4["Download Result"]
        UC5["Share on Social"]
        UC6["Manage Account"]
        UC7["View Analytics"]
        UC8["Manage Payment"]
        UC9["System Admin"]
    end
    
    subgraph External["External Services"]
        E1["Google OAuth"]
        E2["Razorpay Payment"]
        E3["WhatsApp API"]
        E4["Instagram API"]
    end
    
    U1 --> UC1
    U1 --> UC2
    U1 --> UC3
    U1 --> UC4
    U1 --> UC6
    
    U2 --> UC1
    U2 --> UC2
    U2 --> UC3
    U2 --> UC4
    U2 --> UC5
    U2 --> UC6
    U2 --> UC7
    U2 --> UC8
    
    U3 --> UC9
    U3 --> UC7
    U3 --> UC8
    
    UC1 --> E1
    UC3 -.->|AI Processing| System
    UC4 --> UC1
    UC5 --> E3
    UC5 --> E4
    UC8 --> E2
    
    style System fill:#e1f5ff
    style External fill:#fff3e0
    style Users fill:#f3e5f5
```

## Description
- **Free Users**: Can upload, select styles, process images, download standard quality, and manage accounts
- **Premium Users**: Have access to all features including 4K downloads, social sharing, and analytics
- **Admin**: Manages system, views analytics, and payment processing
- **External Services**: Integration with Google OAuth, Razorpay, WhatsApp, and Instagram APIs
