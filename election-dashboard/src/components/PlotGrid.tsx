import React from 'react';
import ImageViewer from './ImageViewer';

interface ImageItem {
  src: string;
  title: string;
}

interface PlotGridProps {
  images: ImageItem[];
  columns?: 2 | 3 | 4;
}

const GRID_COLS: Record<number, string> = {
  2: 'grid-cols-1 sm:grid-cols-2',
  3: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3',
  4: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4',
};

const PlotGrid: React.FC<PlotGridProps> = ({ images, columns = 3 }) => {
  if (!images || images.length === 0) {
    return (
      <div className="flex items-center justify-center py-12 text-slate-400">
        <p className="text-sm">No images to display.</p>
      </div>
    );
  }

  return (
    <div className={`grid ${GRID_COLS[columns]} gap-4`}>
      {images.map((img, idx) => (
        <ImageViewer key={idx} src={img.src} title={img.title} />
      ))}
    </div>
  );
};

export default PlotGrid;
