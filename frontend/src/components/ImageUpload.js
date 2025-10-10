import React, { useState, useCallback, useRef } from 'react';
import { Upload, X, Image as ImageIcon, AlertCircle, CheckCircle, Camera, Folder } from 'lucide-react';

const ImageUpload = ({ 
  onImagesChange, 
  maxImages = 5, 
  maxSizeMB = 5,
  acceptedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'],
  className = '',
  disabled = false,
  showPreview = true,
  allowCamera = true
}) => {
  const [images, setImages] = useState([]);
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [errors, setErrors] = useState([]);
  const fileInputRef = useRef(null);
  const cameraInputRef = useRef(null);

  const validateFile = (file) => {
    const errors = [];
    
    // Check file type
    if (!acceptedTypes.includes(file.type)) {
      errors.push(`File type ${file.type} not supported`);
    }
    
    // Check file size
    const sizeMB = file.size / (1024 * 1024);
    if (sizeMB > maxSizeMB) {
      errors.push(`File size ${sizeMB.toFixed(1)}MB exceeds ${maxSizeMB}MB limit`);
    }
    
    return errors;
  };

  const processFiles = useCallback(async (files) => {
    if (disabled) return;
    
    const fileArray = Array.from(files);
    const newErrors = [];
    const validFiles = [];
    
    // Check total count
    if (images.length + fileArray.length > maxImages) {
      newErrors.push(`Cannot upload more than ${maxImages} images`);
      setErrors(newErrors);
      return;
    }
    
    setUploading(true);
    
    for (const file of fileArray) {
      const fileErrors = validateFile(file);
      if (fileErrors.length > 0) {
        newErrors.push(...fileErrors.map(error => `${file.name}: ${error}`));
        continue;
      }
      
      // Create preview
      const reader = new FileReader();
      const imagePromise = new Promise((resolve) => {
        reader.onload = (e) => {
          const imageData = {
            id: Date.now() + Math.random(),
            file,
            preview: e.target.result,
            name: file.name,
            size: file.size,
            uploaded: false
          };
          resolve(imageData);
        };
        reader.readAsDataURL(file);
      });
      
      validFiles.push(await imagePromise);
    }
    
    const updatedImages = [...images, ...validFiles];
    setImages(updatedImages);
    setErrors(newErrors);
    setUploading(false);
    
    if (onImagesChange) {
      onImagesChange(updatedImages);
    }
  }, [images, maxImages, maxSizeMB, acceptedTypes, disabled, onImagesChange]);

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFiles(e.dataTransfer.files);
    }
  }, [processFiles]);

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      processFiles(e.target.files);
    }
  };

  const removeImage = (imageId) => {
    const updatedImages = images.filter(img => img.id !== imageId);
    setImages(updatedImages);
    if (onImagesChange) {
      onImagesChange(updatedImages);
    }
  };

  const openFileDialog = () => {
    fileInputRef.current?.click();
  };

  const openCamera = () => {
    cameraInputRef.current?.click();
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Upload Area */}
      <div
        className={`
          relative border-2 border-dashed rounded-xl p-6 text-center transition-all duration-200
          ${dragActive 
            ? 'border-blue-500 bg-blue-50' 
            : 'border-gray-300 hover:border-gray-400'
          }
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        `}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={openFileDialog}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept={acceptedTypes.join(',')}
          onChange={handleFileInput}
          className="hidden"
          disabled={disabled}
        />
        
        <input
          ref={cameraInputRef}
          type="file"
          accept="image/*"
          capture="environment"
          onChange={handleFileInput}
          className="hidden"
          disabled={disabled}
        />

        <div className="space-y-4">
          <div className="flex justify-center">
            <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center">
              <Upload className="w-6 h-6 text-gray-400" />
            </div>
          </div>
          
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Upload Images
            </h3>
            <p className="text-sm text-gray-600">
              Drag and drop images here, or click to select files
            </p>
            <p className="text-xs text-gray-500 mt-1">
              Max {maxImages} images • {maxSizeMB}MB each • JPG, PNG, WebP
            </p>
          </div>
          
          {/* Mobile-friendly buttons */}
          <div className="flex flex-col sm:flex-row gap-2 justify-center max-w-xs mx-auto">
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                openFileDialog();
              }}
              disabled={disabled}
              className="btn-outline btn-mobile-full sm:btn-outline flex items-center justify-center text-sm"
            >
              <Folder className="w-4 h-4 mr-2" />
              Choose Files
            </button>
            
            {allowCamera && (
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  openCamera();
                }}
                disabled={disabled}
                className="btn-outline btn-mobile-full sm:btn-outline flex items-center justify-center text-sm"
              >
                <Camera className="w-4 h-4 mr-2" />
                Take Photo
              </button>
            )}
          </div>
        </div>
        
        {uploading && (
          <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center rounded-xl">
            <div className="loading-spinner w-8 h-8" />
          </div>
        )}
      </div>

      {/* Error Messages */}
      {errors.length > 0 && (
        <div className="space-y-2">
          {errors.map((error, index) => (
            <div key={index} className="flex items-center p-3 bg-red-50 border border-red-200 rounded-lg">
              <AlertCircle className="w-4 h-4 text-red-600 mr-2 flex-shrink-0" />
              <span className="text-sm text-red-700">{error}</span>
            </div>
          ))}
        </div>
      )}

      {/* Image Previews */}
      {showPreview && images.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-medium text-gray-900">
              Selected Images ({images.length}/{maxImages})
            </h4>
            <button
              type="button"
              onClick={() => {
                setImages([]);
                if (onImagesChange) onImagesChange([]);
              }}
              className="text-xs text-red-600 hover:text-red-800"
            >
              Clear All
            </button>
          </div>
          
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
            {images.map((image) => (
              <div key={image.id} className="relative group">
                <div className="relative aspect-square bg-gray-100 rounded-lg overflow-hidden">
                  <img
                    src={image.preview}
                    alt={image.name}
                    className="w-full h-full object-cover"
                  />
                  
                  {/* Remove button */}
                  <button
                    type="button"
                    onClick={() => removeImage(image.id)}
                    className="absolute top-1 right-1 w-6 h-6 bg-red-600 text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-200 hover:bg-red-700"
                  >
                    <X className="w-3 h-3" />
                  </button>
                  
                  {/* Status indicator */}
                  <div className="absolute bottom-1 right-1">
                    {image.uploaded ? (
                      <CheckCircle className="w-4 h-4 text-green-600" />
                    ) : (
                      <div className="w-4 h-4 bg-gray-400 rounded-full animate-pulse" />
                    )}
                  </div>
                </div>
                
                {/* Image info */}
                <div className="mt-1">
                  <p className="text-xs text-gray-600 truncate">{image.name}</p>
                  <p className="text-xs text-gray-500">
                    {(image.size / 1024 / 1024).toFixed(1)} MB
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Upload Progress */}
      {uploading && (
        <div className="flex items-center justify-center p-4 bg-blue-50 rounded-lg">
          <div className="loading-spinner w-5 h-5 mr-3" />
          <span className="text-sm text-blue-700">Processing images...</span>
        </div>
      )}
    </div>
  );
};

export default ImageUpload;