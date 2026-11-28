import React, { useState, useCallback } from 'react';
import { ZoomIn, ZoomOut, Maximize2, Download, X, AlertTriangle } from 'lucide-react';

interface ImageViewerProps {
  src: string;
  title: string;
  className?: string;
}

const ImageViewer: React.FC<ImageViewerProps> = ({ src, title, className = '' }) => {
  const [zoom, setZoom] = useState(1);
  const [lightbox, setLightbox] = useState(false);
  const [error, setError] = useState(false);

  const handleZoomIn = () => setZoom((z) => Math.min(z + 0.25, 3));
  const handleZoomOut = () => setZoom((z) => Math.max(z - 0.25, 0.5));
  const handleFullscreen = () => setLightbox(true);
  const handleCloseLightbox = () => setLightbox(false);

  const handleDownload = useCallback(() => {
    const link = document.createElement('a');
    link.href = src;
    link.download = title.replace(/\s+/g, '_') + '.png';
    link.click();
  }, [src, title]);

  const handleError = () => setError(true);

  return (
    <>
      <div className={`bg-white rounded-xl border border-slate-100 shadow-sm overflow-hidden ${className}`}>
        {/* Toolbar */}
        <div className="flex items-center justify-between px-3 py-2 border-b border-slate-100 bg-slate-50">
          <span className="text-xs text-slate-500 font-medium truncate max-w-[60%]">{title}</span>
          <div className="flex items-center gap-1">
            <button
              onClick={handleZoomOut}
              className="p-1 rounded hover:bg-slate-200 text-slate-500 hover:text-slate-800 transition-colors"
              title="Zoom Out"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <span className="text-xs text-slate-400 w-10 text-center">{Math.round(zoom * 100)}%</span>
            <button
              onClick={handleZoomIn}
              className="p-1 rounded hover:bg-slate-200 text-slate-500 hover:text-slate-800 transition-colors"
              title="Zoom In"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={handleFullscreen}
              className="p-1 rounded hover:bg-slate-200 text-slate-500 hover:text-slate-800 transition-colors"
              title="Fullscreen"
            >
              <Maximize2 className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={handleDownload}
              className="p-1 rounded hover:bg-slate-200 text-slate-500 hover:text-slate-800 transition-colors"
              title="Download"
            >
              <Download className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Image area */}
        <div className="overflow-auto max-h-80 flex items-center justify-center bg-slate-50 p-2 min-h-32">
          {error ? (
            <div className="flex flex-col items-center justify-center gap-2 text-slate-400 py-6">
              <AlertTriangle className="w-8 h-8" />
              <span className="text-sm font-medium">Image not available</span>
              <span className="text-xs text-slate-300 max-w-48 text-center break-all">{src}</span>
            </div>
          ) : (
            <img
              src={src}
              alt={title}
              onError={handleError}
              style={{ transform: `scale(${zoom})`, transformOrigin: 'top left', transition: 'transform 0.2s' }}
              className="max-w-full object-contain cursor-zoom-in"
              onClick={handleFullscreen}
            />
          )}
        </div>

        {/* Title below */}
        <div className="px-3 py-2 border-t border-slate-100">
          <p className="text-xs text-slate-600 text-center font-medium">{title}</p>
        </div>
      </div>

      {/* Lightbox */}
      {lightbox && (
        <div
          className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4"
          onClick={handleCloseLightbox}
        >
          <div
            className="relative max-w-5xl max-h-screen overflow-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              onClick={handleCloseLightbox}
              className="absolute top-2 right-2 bg-white/10 hover:bg-white/20 text-white rounded-full p-1 z-10 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
            {error ? (
              <div className="bg-slate-800 rounded-xl p-16 flex flex-col items-center gap-3 text-slate-300">
                <AlertTriangle className="w-12 h-12" />
                <span className="text-lg font-medium">Image not available</span>
              </div>
            ) : (
              <img src={src} alt={title} className="rounded-lg max-h-screen object-contain" />
            )}
            <p className="text-white/70 text-sm text-center mt-3">{title}</p>
          </div>
        </div>
      )}
    </>
  );
};

export default ImageViewer;
