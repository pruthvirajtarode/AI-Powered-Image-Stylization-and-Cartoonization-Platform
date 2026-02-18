# AI POWERED IMAGE STYLIZATION AND CARTOONIZATION - SYSTEM FLOW

```mermaid
graph TD
    %% Entry Point
    Start((User Upload)) --> Input[Upload Multiple Images]
    
    %% Client Side
    subgraph Frontend [AI Studio Dashboard]
        Input --> BatchQueue[Batch Queue Management]
        BatchQueue --> StyleSelection{Select Style per Image}
        StyleSelection -->|Cartoon| C1[Apply Classic parameters]
        StyleSelection -->|Anime| C2[Apply Neo-Anime config]
        StyleSelection -->|Sketch| C3[Apply Graphite config]
        ProcessBtn[Launch Transformation] --> APIRequest[/POST /api/process/batch/]
    end

    %% Server Side
    subgraph Backend [Neural Processing Engine]
        APIRequest --> AuthCheck{Verify Auth & Credits}
        AuthCheck -->|No| LoginModal[Redirect to Auth]
        AuthCheck -->|Yes| ParallelProc[Parallel Processing Thread]
        
        subgraph Pipeline [Stylization Pipeline]
            ParallelProc --> PreScale[Auto-Resize & Pre-processing]
            
            %% Canny Edge Detection logic from User's Research
            PreScale --> EdgeDet[Edge Detection Pipeline]
            subgraph Edges [Canny Edge Detection Workflow]
                EdgeDet --> GBlur[1. Gaussian Blur: Noise Removal]
                GBlur --> Gradient[2. Gradient Calculation]
                Gradient --> NMS[3. Non-Maximum Suppression]
                NMS --> DThresh[4. Double Thresholding]
                DThresh --> Hysteresis[5. Hysteresis Tracking]
            end
            
            PreScale --> ColorQ[K-Means Color Quantization]
            Edges --> Merge[Neural Composition Layer]
            ColorQ --> Merge
        end
        
        Merge --> StatsEngine[Neural Analysis: Brightness/Contrast/Color]
        StatsEngine --> DB[(Save to ImageHistory & Disk)]
    end

    %% Results
    DB --> Response[JSON Response with URLs]
    Response --> BatchGrid[Render Batch Results Grid]
    BatchGrid --> ViewResult[Comparison Stage: Side-by-Side]
    ViewResult --> Export{Paid Export?}
    Export -->|Yes| HDDownload[HD Download JPG/PNG/PDF]
    Export -->|No| Watermark[Watermarked Preview]
```

## Detailed Neural Stylization Steps

### 1. Pre-processing
The engine automatically scales high-resolution images to the optimal processing size (ideal for 720p/1080p) to maintain real-time performance without losing structural detail.

### 2. Canny Edge Detection (Structural Integrity)
As seen in the technical research, the engine extracts the "soul" of the image by:
*   **Gaussian Smoothing**: Eliminating high-frequency noise.
*   **Magnitude Thresholding**: Identifying only the most relevant artistic lines.
*   **Hysteresis**: Ensuring continuous, flowing outlines typical of hand-drawn art.

### 3. Color Quantization
Using **K-Means Clustering**, the original millions of colors are condensed into a curated palette (usually 6-16 colors). This creates the "Flat" or "Posterized" look essential for cartoons and anime.

### 4. Neural Analysis (Task 13)
Every image is analyzed for:
*   **Brightness**: Ensuring the artistic output isn't too dark.
*   **Contrast**: Maintaining the "pop" of the stylization.
*   **Color Balance**: Tracking the dominant hues (Red, Green, Blue).

---
*Generated for the AI-Powered Image Stylization and Cartoonization Platform*
