# Sequence Diagram - Image Stylization Flow

```mermaid
sequenceDiagram
    participant User as 👤 User
    participant Frontend as 🖥️ Frontend
    participant Flask as 🚀 Flask Backend
    participant Auth as 🔐 Authentication
    participant ImageProc as 🎨 Image Processing
    participant DB as 💾 Database
    participant Payment as 💳 Payment
    participant Export as 📤 Export Service
    
    User->>Frontend: Upload Image
    Frontend->>Flask: POST /upload
    Flask->>Auth: Verify Session
    Auth->>DB: Check User Plan
    DB-->>Auth: User Premium?
    Auth-->>Flask: ✓ Authenticated
    
    User->>Frontend: Select Style
    Frontend->>Flask: POST /process (style='pixar')
    Flask->>ImageProc: load_image()
    ImageProc->>ImageProc: Apply OpenCV Filters
    ImageProc->>ImageProc: Apply Neural Style
    ImageProc-->>Flask: Processed Image Buffer
    
    Flask->>DB: Save Processing Record
    Flask->>Frontend: Return Preview
    Frontend-->>User: Display Styled Image
    
    User->>Frontend: Download 4K
    Frontend->>Flask: GET /download?quality=4k
    Flask->>Payment: Check Premium Access
    Payment-->>Flask: ✓ Authorized
    Flask->>ImageProc: Render 4K Quality
    ImageProc-->>Flask: 4K Image File
    Flask->>Export: Generate Download Link
    Export-->>Flask: Download URL Ready
    Flask-->>Frontend: Send File
    Frontend-->>User: ⬇️ Download Complete
    
    User->>Frontend: Share on WhatsApp
    Frontend->>Flask: POST /export/whatsapp
    Flask->>Export: Generate QR & Link
    Export->>Export: Compress for WhatsApp
    Export-->>Flask: WhatsApp Link Ready
    Flask-->>Frontend: ✓ Share Link
    Frontend-->>User: Open WhatsApp
```

## Description
This sequence diagram shows the interactions between different components during:
1. **Image Upload & Authentication**: User authenticates and uploads an image
2. **Image Processing**: The image is processed with the selected AI style
3. **Download with Quality Check**: Premium users can download 4K images
4. **Social Media Export**: Users can share stylized images via WhatsApp
