from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import cv2
import numpy as np
from PIL import Image
from PIL.ExifTags import TAGS
import pytesseract
import io
import re
from datetime import datetime
import hashlib
from scipy import ndimage
from skimage import measure, feature
import base64

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


app = Flask(__name__)
CORS(app)

class IndianDocumentForensics:
    def __init__(self):
        self.indian_doc_keywords = [
            'aadhaar', 'aadhar', 'uid', 'uidai', 'government of india',
            'income tax', 'permanent account number', 'pan', 'govt of india',
            'भारत सरकार', 'आधार', 'dob', 'date of birth'
        ]

    def analyze_document(self, image_bytes):
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return {"error": "Invalid image"}

        is_indian_doc, doc_type, confidence = self.detect_indian_document(img)

        results = {
            "is_indian_document": is_indian_doc,
            "document_type": doc_type,
            "document_confidence": confidence,
            "metadata_analysis": self.check_metadata(image_bytes),
            "ai_generation_detection": self.detect_ai_generation(img),
            "manipulation_detection": self.detect_manipulation(img),
            "texture_analysis": self.analyze_texture(img),
            "compression_analysis": self.analyze_compression(img),
            "ocr_validation": self.validate_document_format(img, doc_type),
            "edge_analysis": self.analyze_edges(img),
            "timestamp": datetime.now().isoformat()
        }

        # 🔧 Penalize if not Indian doc, but DO NOT ZERO
        penalty = 30 if not is_indian_doc else 0

        results["overall_score"] = max(
            0,
            self.calculate_overall_score(results) - penalty
        )

        results["verdict"] = self.get_verdict(results["overall_score"])
        results["risk_level"] = self.get_risk_level(results["overall_score"])

        return results

            
    
    def detect_indian_document(self, img):
        """Detect if image is an Indian document (Aadhaar/PAN)"""
        try:
            # Convert to RGB for OCR
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb)
            
            # OCR text extraction
            text = pytesseract.image_to_string(pil_img).lower()
            
            # Count keyword matches
            keyword_matches = sum(1 for keyword in self.indian_doc_keywords if keyword in text)
            
            # Detect document type
            doc_type = "Unknown"
            if any(kw in text for kw in ['aadhaar', 'aadhar', 'uid', 'uidai']):
                doc_type = "Aadhaar Card"
            elif any(kw in text for kw in ['permanent account', 'income tax', 'pan']):
                doc_type = "PAN Card"
            
            # Check for Aadhaar number pattern (12 digits with spaces)
            aadhaar_pattern = r'\d{4}\s\d{4}\s\d{4}'
            has_aadhaar_num = bool(re.search(aadhaar_pattern, text))
            
            # Check for PAN pattern (ABCDE1234F)
            pan_pattern = r'[A-Z]{5}\d{4}[A-Z]'
            has_pan_num = bool(re.search(pan_pattern, text))
            
            # Calculate confidence
            confidence = 0
            if keyword_matches >= 2:
                confidence += 40
            if has_aadhaar_num or has_pan_num:
                confidence += 40
            if doc_type != "Unknown":
                confidence += 20
            
            # Check color scheme (Indian docs have specific colors)
            avg_color = np.mean(img, axis=(0, 1))
            if self.check_indian_doc_colors(avg_color, doc_type):
                confidence += 10
            
            is_indian_doc = confidence >= 50
            
            return is_indian_doc, doc_type, confidence
            
        except Exception as e:
            return False, "Unknown", 0
    
    def check_indian_doc_colors(self, avg_color, doc_type):
        """Check if color scheme matches Indian documents"""
        # Aadhaar: predominantly white/light blue
        # PAN: predominantly cream/light yellow
        if doc_type == "Aadhaar Card":
            return avg_color[2] > 150  # High blue/white
        elif doc_type == "PAN Card":
            return avg_color[0] > 140 and avg_color[1] > 140  # Cream/yellow
        return False
    
    def check_metadata(self, image_bytes):
        """Analyze EXIF metadata for manipulation signs"""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            exif_data = image._getexif() or {}
            
            metadata = {}
            suspicious_indicators = []
            score = 100
            
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                metadata[tag] = str(value)
            
            # Check for editing software
            software = metadata.get('Software', '').lower()
            editing_tools = ['photoshop', 'gimp', 'paint.net', 'pixelmator', 
                           'affinity', 'canva', 'midjourney', 'dall-e', 'stable diffusion']
            
            for tool in editing_tools:
                if tool in software:
                    suspicious_indicators.append(f"Edited with: {tool}")
                    score -= 30
            
            # Check if metadata is missing (AI generated often lacks metadata)
            if len(metadata) < 5:
                suspicious_indicators.append("Missing EXIF metadata (common in AI-generated images)")
                score -= 8
            
            # Check creation date
            if 'DateTime' in metadata:
                try:
                    create_date = datetime.strptime(metadata['DateTime'], '%Y:%m:%d %H:%M:%S')
                    if (datetime.now() - create_date).days < 7:
                        suspicious_indicators.append("Document created very recently")
                        score -= 10
                except:
                    pass
            
            return {
                "score": max(0, score),
                "metadata_present": len(metadata) > 0,
                "metadata_count": len(metadata),
                "suspicious_indicators": suspicious_indicators,
                "software_used": metadata.get('Software', 'Not specified'),
                "creation_date": metadata.get('DateTime', 'Not available')
            }
            
        except Exception as e:
            return {
                "score": 20,
                "metadata_present": False,
                "error": "No EXIF metadata found (highly suspicious)",
                "suspicious_indicators": ["No metadata - likely AI-generated or heavily edited"]
            }
    
    def detect_ai_generation(self, img):
        """Detect AI generation patterns"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        score = 70
        indicators = []
        
        # Check for unnatural smoothness
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        if laplacian_var < 100:
            indicators.append("Unnaturally smooth - possible AI generation")
            score -= 20
        
        # Check for JPEG artifacts inconsistency
        dct = cv2.dct(np.float32(gray))
        dct_variance = np.var(dct)
        if dct_variance > 10000:
            indicators.append("Inconsistent compression artifacts")
            score -= 20
        
        # Check for perfect edges (AI-generated images often have too-perfect edges)
        edges = cv2.Canny(gray, 50, 150)
        edge_ratio = np.sum(edges > 0) / edges.size
        if edge_ratio < 0.01 or edge_ratio > 0.3:
            indicators.append("Artificial edge patterns detected")
            score -= 25
        
        return {
            "score": max(0, score),
            "ai_indicators": indicators,
            "smoothness_variance": float(laplacian_var),
            "edge_ratio": float(edge_ratio)
        }
    
    def detect_manipulation(self, img):
        """Detect copy-paste and cloning"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        score = 70
        indicators = []
        
        # Error Level Analysis (ELA) simulation
        _, encoded = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 90])
        recompressed = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
        ela = cv2.absdiff(img, recompressed)
        ela_gray = cv2.cvtColor(ela, cv2.COLOR_BGR2GRAY)
        
        # Check for suspicious regions with different compression levels
        _, thresh = cv2.threshold(ela_gray, 30, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        large_regions = [c for c in contours if cv2.contourArea(c) > 1000]
        if len(large_regions) > 5:
            indicators.append(f"Found {len(large_regions)} regions with compression inconsistency")
            score -= 30
        
        # Clone detection using feature matching
        orb = cv2.ORB_create()
        kp = orb.detect(gray, None)
        if len(kp) < 50:
            indicators.append("Insufficient unique features - possible duplication")
            score -= 20
        
        return {
            "score": max(0, score),
            "manipulation_indicators": indicators,
            "suspicious_regions": len(large_regions),
            "unique_features": len(kp)
        }
    
    def analyze_texture(self, img):
        """Analyze texture patterns for over-smoothing"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        score = 70
        indicators = []
        
        # Calculate texture using Gabor filters
        angles = [0, 45, 90, 135]
        textures = []
        for angle in angles:
            kernel = cv2.getGaborKernel((21, 21), 5, np.radians(angle), 10, 0.5, 0)
            filtered = cv2.filter2D(gray, cv2.CV_32F, kernel)
            textures.append(np.var(filtered))
        
        avg_texture = np.mean(textures)
        
        # Natural documents have texture variance
        if avg_texture < 50:
            indicators.append("Over-smoothed texture - likely AI-generated")
            score -= 15
        
        # Check for artificial sharpness
        gradient = np.gradient(gray.astype(float))
        gradient_mag = np.sqrt(gradient[0]**2 + gradient[1]**2)
        sharpness = np.mean(gradient_mag)
        
        if sharpness > 30:
            indicators.append("Artificial sharpening detected")
            score -= 20
        
        return {
            "score": max(0, score),
            "texture_indicators": indicators,
            "texture_variance": float(avg_texture),
            "sharpness_level": float(sharpness)
        }
    
    def analyze_compression(self, img):
        """Analyze compression artifacts"""
        score = 70
        indicators = []
        
        # Analyze DCT coefficients for JPEG compression
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Check 8x8 block artifacts (JPEG compression signature)
        blocks = []
        for i in range(0, gray.shape[0] - 8, 8):
            for j in range(0, gray.shape[1] - 8, 8):
                block = gray[i:i+8, j:j+8]
                blocks.append(np.std(block))
        
        block_variance = np.var(blocks)
        
        if block_variance < 10:
            indicators.append("Uniform compression - digitally generated")
            score -= 10
        
        # Real scanned documents have noise
        noise_level = np.std(gray)
        if noise_level < 15:
            indicators.append("Too clean - missing natural noise")
            score -= 25
        
        return {
            "score": max(0, score),
            "compression_indicators": indicators,
            "block_variance": float(block_variance),
            "noise_level": float(noise_level)
        }
    
    def validate_document_format(self, img, doc_type):
        """OCR validation of Aadhaar/PAN format"""
        score = 70
        indicators = []
        
        try:
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb)
            text = pytesseract.image_to_string(pil_img)
            
            if doc_type == "Aadhaar Card":
                # Validate Aadhaar number format (12 digits)
                aadhaar_pattern = r'\d{4}\s\d{4}\s\d{4}'
                matches = re.findall(aadhaar_pattern, text)
                
                if not matches:
                    indicators.append("Aadhaar number format not found")
                    score -= 40
                else:
                    # Validate checksum (Verhoeff algorithm)
                    aadhaar_num = matches[0].replace(' ', '')
                    if not self.validate_aadhaar_checksum(aadhaar_num):
                        indicators.append("Invalid Aadhaar checksum")
                        score -= 30
                
            elif doc_type == "PAN Card":
                # Validate PAN format (ABCDE1234F)
                pan_pattern = r'[A-Z]{5}\d{4}[A-Z]'
                matches = re.findall(pan_pattern, text)
                
                if not matches:
                    indicators.append("PAN number format not found")
                    score -= 40
                else:
                    # Validate PAN structure
                    pan = matches[0]
                    if pan[3] not in 'PCHFATBLJG':  # 4th char must be status code
                        indicators.append("Invalid PAN structure")
                        score -= 30
            
            # Check for mandatory fields
            mandatory_terms = ['date of birth', 'dob', 'father', 'name']
            found_terms = sum(1 for term in mandatory_terms if term in text.lower())
            
            if found_terms < 2:
                indicators.append("Missing mandatory fields")
                score -= 20
            
            return {
                "score": max(0, score),
                "format_indicators": indicators,
                "extracted_text_length": len(text),
                "mandatory_fields_found": found_terms
            }
            
        except Exception as e:
            return {
                "score": 50,
                "error": "OCR processing failed",
                "format_indicators": ["Could not validate format"]
            }
    
    def validate_aadhaar_checksum(self, aadhaar):
        """Validate Aadhaar using Verhoeff algorithm"""
        try:
            # Verhoeff algorithm multiplication table
            d = [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                 [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
                 [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
                 [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
                 [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
                 [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
                 [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
                 [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
                 [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
                 [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]]
            
            p = [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                 [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
                 [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
                 [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
                 [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
                 [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
                 [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
                 [7, 0, 4, 6, 9, 1, 3, 2, 5, 8]]
            
            c = 0
            for i, digit in enumerate(reversed(aadhaar)):
                c = d[c][p[(i % 8)][int(digit)]]
            
            return c == 0
        except:
            return False
    
    def analyze_edges(self, img):
        """Analyze edge patterns for artificial generation"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        score = 100
        indicators = []
        
        # Canny edge detection
        edges = cv2.Canny(gray, 100, 200)
        
        # Natural documents have irregular edges
        edge_pixels = np.sum(edges > 0)
        total_pixels = edges.size
        edge_density = edge_pixels / total_pixels
        
        # Check for too-perfect edges
        if edge_density < 0.02:
            indicators.append("Too few edges - possible AI generation")
            score -= 25
        
        # Check edge straightness
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
        if lines is not None and len(lines) > 50:
            indicators.append("Excessive straight lines - artificial")
            score -= 20
        
        return {
            "score": max(0, score),
            "edge_indicators": indicators,
            "edge_density": float(edge_density),
            "straight_lines": len(lines) if lines is not None else 0
        }
    
    def calculate_overall_score(self, results):
        """Calculate weighted overall authenticity score"""
        if not results.get("is_indian_document", False):
            return 0
        
        weights = {
            "metadata_analysis": 0.15,
            "ai_generation_detection": 0.25,
            "manipulation_detection": 0.20,
            "texture_analysis": 0.15,
            "compression_analysis": 0.10,
            "ocr_validation": 0.10,
            "edge_analysis": 0.05
        }
        
        total = 0
        weight_sum = 0

        for k, w in weights.items():
         if k in results and "score" in results[k]:
             total += results[k]["score"] * w
             weight_sum += w

        final_score = total / weight_sum

        # Boost for real scanned documents
        final_score = min(100, final_score * 1.15)

        return round(final_score, 2)

    
    def get_verdict(self, score):
        """Get final verdict based on score"""
        if score >= 80:
            return "AUTHENTIC - Document appears genuine"
        elif score >= 60:
            return "SUSPICIOUS - Manual review recommended"
        elif score >= 40:
            return "HIGHLY SUSPICIOUS - Likely manipulated"
        else:
            return "REJECTED - Likely AI-generated or fake"
    
    def get_risk_level(self, score):
        """Get risk level"""
        if score >= 80:
            return "Low"
        elif score >= 60:
            return "Medium"
        elif score >= 40:
            return "High"
        else:
            return "Critical"

# Initialize forensics analyzer
forensics = IndianDocumentForensics()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        if 'document' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['document']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Read file bytes
        image_bytes = file.read()
        
        # Analyze document
        results = forensics.analyze_document(image_bytes)
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "Layer 1 Document Forensics"})
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for orchestrator"""
    return jsonify({
        "status": "healthy",
        "service": "Layer 1 - Document Forensics",
        "version": "1.0.0"
    }), 200
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)