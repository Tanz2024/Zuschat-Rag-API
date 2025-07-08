import React from 'react'
import Image from 'next/image'

interface Product {
  id: string
  name: string
  price?: string
  image?: string
  description?: string
  category?: string
  availability?: boolean
}

interface ProductCardProps {
  product: Product
  onClick?: (product: Product) => void
}

const ProductCard: React.FC<ProductCardProps> = ({ product, onClick }) => {
  return (
    <div 
      className="product-card cursor-pointer group fade-in"
      onClick={() => onClick?.(product)}
    >
      {/* Product Image */}
      {product.image && (
        <div className="aspect-w-16 aspect-h-9 mb-3">
          <Image
            src={product.image}
            alt={product.name}
<<<<<<< HEAD
            width={300}
            height={200}
=======
            width={320}
            height={128}
>>>>>>> 045029b (fixes)
            className="w-full h-32 object-cover rounded-lg"
            onError={(e) => {
              const target = e.target as HTMLImageElement
              target.src = '/placeholder-product.jpg'
            }}
          />
        </div>
      )}
      
      {/* Product Info */}
      <div className="space-y-2">
        <div className="flex items-start justify-between">
          <h3 className="font-semibold text-gray-900 dark:text-white text-sm group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors duration-200">
            {product.name}
          </h3>
          {product.availability !== undefined && (
            <span className={`text-xs px-2 py-1 rounded-full ${
              product.availability 
                ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300' 
                : 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300'
            }`}>
              {product.availability ? 'Available' : 'Out of Stock'}
            </span>
          )}
        </div>
        
        {product.description && (
          <p className="text-gray-600 dark:text-gray-300 text-xs line-clamp-2 transition-colors duration-300">
            {product.description}
          </p>
        )}
        
        <div className="flex items-center justify-between">
          {product.price && (
            <span className="font-bold text-blue-600 dark:text-blue-400">
              {product.price}
            </span>
          )}
          
          {product.category && (
            <span className="text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 px-2 py-1 rounded transition-colors duration-300">
              {product.category}
            </span>
          )}
        </div>
      </div>
      
      {/* Hover Effect */}
      <div className="absolute inset-0 bg-blue-500 bg-opacity-0 group-hover:bg-opacity-5 dark:group-hover:bg-opacity-10 rounded-xl transition-all duration-200"></div>
    </div>
  )
}

export default ProductCard
