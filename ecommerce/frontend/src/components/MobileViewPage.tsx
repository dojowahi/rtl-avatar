import { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Button, 
  IconButton, 
  Card, 
  CardContent, 
  CardMedia, 
  Chip, 
  Badge, 
  Dialog, 
  DialogContent
} from '@mui/material';
import React from 'react';
import { 
  ArrowBack, 
  Home, 
  ShoppingCart, 
  Person, 
  Star, 
  Close, 
  AddShoppingCart,
  Wifi,
  BatteryFull,
  SignalCellularAlt,
  GraphicEq,
  PlayArrow,
  Stop
} from '@mui/icons-material';
import { useGeminiLive } from '../hooks/useGeminiLive';
import { AvatarDisplay1P } from './AvatarDisplay1P';

interface MobileViewPageProps {
  navigate: (to: string) => void;
  products: any[];
  configData?: any;
}

export function MobileViewPage({ navigate, products: initialProducts }: MobileViewPageProps) {
  const [products, setProducts] = useState<any[]>(initialProducts || []);
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [selectedProduct, setSelectedProduct] = useState<any | null>(null);
  const [cartCount, setCartCount] = useState<number>(0);
  const [activeBottomTab, setActiveBottomTab] = useState<number>(0);
  const [sessionId] = useState(`mob_${Math.random().toString(36).substring(2, 9)}`);
  const { connectionState, connect, disconnect, config } = useGeminiLive('google_1p', sessionId);

  useEffect(() => {
    if (products.length === 0) {
      fetch('/api/products')
        .then(res => res.json())
        .then(data => {
          if (Array.isArray(data)) setProducts(data);
        })
        .catch(err => console.error("Failed to load products in mobile view:", err));
    }
  }, [products.length]);

  const categories = ['All', 'Electronics', 'Fashion', 'Home Decor', 'Appliances'];

  const filteredProducts = selectedCategory === 'All' 
    ? products 
    : products.filter(p => (p.category || '').toLowerCase().includes(selectedCategory.toLowerCase()));

  const handleAddToCart = (e: React.MouseEvent, _prod: any) => {
    e.stopPropagation();
    setCartCount(prev => prev + 1);
  };

  return (
    <Box sx={{ 
      minHeight: '100vh', 
      bgcolor: '#0b0f19', 
      color: '#f8fafc', 
      py: 4, 
      px: { xs: 2, md: 6 },
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center'
    }}>
      {/* Top Header Controls */}
      <Box sx={{ width: '100%', maxWidth: 1000, display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h5" sx={{ fontWeight: '900', letterSpacing: '-0.02em', background: 'linear-gradient(90deg, #6366f1 0%, #a855f7 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            MOBILE APP EXPERIENCE
          </Typography>
          <Typography variant="caption" sx={{ color: '#94a3b8' }}>
            Interactive smartphone simulator for responsive e-commerce shopping
          </Typography>
        </Box>
        <Button 
          variant="outlined" 
          startIcon={<ArrowBack />} 
          onClick={() => navigate('/')}
          sx={{ 
            color: '#ffffff', 
            borderColor: 'rgba(255,255,255,0.2)', 
            borderRadius: '24px',
            textTransform: 'none',
            px: 3,
            '&:hover': { borderColor: '#6366f1', bgcolor: 'rgba(99, 102, 241, 0.1)' }
          }}
        >
          Back to Desktop Store
        </Button>
      </Box>

      {/* Smartphone Device Simulator Container */}
      <Box sx={{
        width: 380,
        height: 780,
        bgcolor: '#000000',
        borderRadius: '50px',
        p: '14px',
        boxShadow: '0 25px 60px rgba(0, 0, 0, 0.8), 0 0 40px rgba(99, 102, 241, 0.2)',
        border: '4px solid #334155',
        position: 'relative',
        display: 'flex',
        flexDirection: 'column'
      }}>
        {/* Inner Phone Screen */}
        <Box sx={{
          flexGrow: 1,
          bgcolor: '#f8fafc',
          color: '#0f172a',
          borderRadius: '38px',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
          position: 'relative'
        }}>
          
          {/* Status Bar */}
          <Box sx={{ 
            bgcolor: '#ffffff', 
            pt: 1.5, 
            pb: 1, 
            px: 3, 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            fontSize: '12px',
            fontWeight: '800'
          }}>
            <Typography variant="caption" sx={{ fontWeight: '800' }}>9:41</Typography>
            {/* Dynamic Island / Notch */}
            <Box sx={{ width: 90, height: 20, bgcolor: '#000000', borderRadius: '10px' }} />
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <SignalCellularAlt sx={{ fontSize: 14 }} />
              <Wifi sx={{ fontSize: 14 }} />
              <BatteryFull sx={{ fontSize: 14 }} />
            </Box>
          </Box>

          {/* App Header */}
          <Box sx={{ 
            bgcolor: '#ffffff', 
            px: 2.5, 
            py: 1.5, 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            borderBottom: '1px solid #e2e8f0'
          }}>
            <Typography variant="subtitle1" sx={{ fontWeight: '900', letterSpacing: '-0.5px' }}>
              RETAIL ASSISTANT
            </Typography>
            <IconButton size="small" sx={{ bgcolor: '#f1f5f9' }}>
              <Badge badgeContent={cartCount} color="primary">
                <ShoppingCart fontSize="small" />
              </Badge>
            </IconButton>
          </Box>

          {/* Category Filter Pills */}
          <Box sx={{ 
            display: 'flex', 
            gap: 1, 
            px: 2, 
            py: 1.5, 
            overflowX: 'auto', 
            bgcolor: '#ffffff',
            '&::-webkit-scrollbar': { display: 'none' }
          }}>
            {categories.map((cat) => (
              <Chip
                key={cat}
                label={cat}
                size="small"
                onClick={() => setSelectedCategory(cat)}
                sx={{
                  fontWeight: '700',
                  fontSize: '11px',
                  bgcolor: selectedCategory === cat ? '#000000' : '#f1f5f9',
                  color: selectedCategory === cat ? '#ffffff' : '#475569',
                  '&:hover': { bgcolor: selectedCategory === cat ? '#000000' : '#e2e8f0' }
                }}
              />
            ))}
          </Box>

          {/* Content Area */}
          {activeBottomTab === 1 ? (
            <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', p: 3, bgcolor: '#0f172a', color: '#ffffff', alignItems: 'center', justifyContent: 'center', pb: 9 }}>
              <Box sx={{ width: '100%', maxWidth: 220, aspectRatio: '704/1280', maxHeight: 300, borderRadius: 4, overflow: 'hidden', mb: 3, boxShadow: '0 10px 30px rgba(0,0,0,0.5)', bgcolor: '#1e293b', display: 'flex', justifyContent: 'center' }}>
                <AvatarDisplay1P 
                  status={
                    connectionState === 'connected' ? 'ready' : 
                    connectionState === 'connecting' ? 'initializing' : 'idle'
                  } 
                  useVertexAI={config?.useVertexAI}
                  avatarName={config?.google1PAvatarName || 'Vera'}
                />
              </Box>
              <Typography variant="subtitle1" sx={{ fontWeight: '900', mb: 0.5 }}>
                Meet {config?.google1PAvatarName || 'Vera'} AI Assistant
              </Typography>
              <Typography variant="caption" sx={{ color: '#94a3b8', textAlign: 'center', mb: 3, px: 1, lineHeight: 1.4 }}>
                Tap below to talk with your real-time multimodal shopping concierge.
              </Typography>
              {connectionState !== 'connected' ? (
                <Button 
                  variant="contained" 
                  startIcon={<PlayArrow />} 
                  onClick={connect}
                  sx={{ bgcolor: '#6366f1', borderRadius: '24px', px: 4, py: 1.2, fontWeight: '800', '&:hover': { bgcolor: '#4f46e5' } }}
                >
                  Start Voice Session
                </Button>
              ) : (
                <Button 
                  variant="contained" 
                  color="error"
                  startIcon={<Stop />} 
                  onClick={disconnect}
                  sx={{ borderRadius: '24px', px: 4, py: 1.2, fontWeight: '800' }}
                >
                  End Voice Session
                </Button>
              )}
            </Box>
          ) : (
            <Box sx={{ flexGrow: 1, overflowY: 'auto', p: 2, bgcolor: '#f1f5f9', pb: 8 }}>
              <Typography variant="caption" sx={{ fontWeight: '800', color: '#64748b', mb: 1, display: 'block', textTransform: 'uppercase' }}>
                Featured Products ({filteredProducts.length})
              </Typography>
              
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {filteredProducts.map((prod) => (
                  <Card 
                    key={prod.product_id}
                    onClick={() => setSelectedProduct(prod)}
                    sx={{ 
                      borderRadius: 3, 
                      boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
                      cursor: 'pointer',
                      display: 'flex',
                      overflow: 'hidden',
                      transition: 'transform 0.2s',
                      '&:active': { transform: 'scale(0.98)' }
                    }}
                  >
                    <CardMedia
                      component="img"
                      sx={{ width: 110, objectFit: 'cover', bgcolor: '#e2e8f0' }}
                      image={prod.image_url || '/placeholder.png'}
                      alt={prod.name}
                    />
                    <CardContent sx={{ p: 1.5, flexGrow: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                      <Box>
                        <Typography variant="subtitle2" sx={{ fontWeight: '800', lineHeight: 1.2, mb: 0.5, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                          {prod.name}
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <Star sx={{ fontSize: 14, color: '#f59e0b' }} />
                          <Typography variant="caption" sx={{ fontWeight: '700', color: '#64748b' }}>
                            {prod.rating ? prod.rating.toFixed(1) : '4.8'}
                          </Typography>
                        </Box>
                      </Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1 }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: '900', color: '#000000' }}>
                          ${prod.price ? Number(prod.price).toFixed(2) : '99.99'}
                        </Typography>
                        <IconButton 
                          size="small" 
                          onClick={(e) => handleAddToCart(e, prod)}
                          sx={{ bgcolor: '#000000', color: '#ffffff', '&:hover': { bgcolor: '#333333' } }}
                        >
                          <AddShoppingCart sx={{ fontSize: 16 }} />
                        </IconButton>
                      </Box>
                    </CardContent>
                  </Card>
                ))}
              </Box>
            </Box>
          )}

          {/* Bottom App Navigation Bar */}
          <Box sx={{
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            bgcolor: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(10px)',
            borderTop: '1px solid #e2e8f0',
            py: 1,
            px: 3,
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            zIndex: 10
          }}>
            {[
              { label: 'Home', icon: <Home /> },
              { label: 'Vera AI', icon: <GraphicEq /> },
              { label: 'Cart', icon: <Badge badgeContent={cartCount} color="primary"><ShoppingCart /></Badge> },
              { label: 'Profile', icon: <Person /> }
            ].map((tab, idx) => (
              <Box 
                key={tab.label}
                onClick={() => setActiveBottomTab(idx)}
                sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', cursor: 'pointer', color: activeBottomTab === idx ? '#000000' : '#94a3b8' }}
              >
                {React.cloneElement(tab.icon, { sx: { fontSize: 22 } })}
                <Typography variant="caption" sx={{ fontSize: '10px', fontWeight: activeBottomTab === idx ? '800' : '600', mt: 0.2 }}>
                  {tab.label}
                </Typography>
              </Box>
            ))}
          </Box>

        </Box>
      </Box>

      {/* Product Detail Modal (Mobile Bottom Sheet) */}
      <Dialog
        open={Boolean(selectedProduct)}
        onClose={() => setSelectedProduct(null)}
        slotProps={{
          paper: {
            sx: {
              width: 360,
              borderRadius: '24px 24px 0 0',
              position: 'absolute',
              bottom: 20,
              m: 0,
              maxHeight: '70%',
              bgcolor: '#ffffff',
              color: '#0f172a'
            }
          }
        }}
      >
        {selectedProduct && (
          <DialogContent sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 1 }}>
              <IconButton size="small" onClick={() => setSelectedProduct(null)}>
                <Close fontSize="small" />
              </IconButton>
            </Box>
            <Box sx={{ textAlign: 'center', mb: 2 }}>
              <img 
                src={selectedProduct.image_url || '/placeholder.png'} 
                alt={selectedProduct.name}
                style={{ width: '100%', maxHeight: 180, objectFit: 'contain', borderRadius: 12 }} 
              />
            </Box>
            <Typography variant="h6" sx={{ fontWeight: '900', lineHeight: 1.2, mb: 1 }}>
              {selectedProduct.name}
            </Typography>
            <Typography variant="h5" sx={{ fontWeight: '900', color: '#6366f1', mb: 2 }}>
              ${selectedProduct.price ? Number(selectedProduct.price).toFixed(2) : '99.99'}
            </Typography>
            <Typography variant="body2" sx={{ color: '#475569', lineHeight: 1.6, mb: 3 }}>
              {selectedProduct.description || 'No description available for this item.'}
            </Typography>
            <Button
              fullWidth
              variant="contained"
              startIcon={<AddShoppingCart />}
              onClick={(e) => {
                handleAddToCart(e, selectedProduct);
                setSelectedProduct(null);
              }}
              sx={{ bgcolor: '#000000', color: '#ffffff', py: 1.5, borderRadius: 3, fontWeight: '800', '&:hover': { bgcolor: '#333333' } }}
            >
              Add to Mobile Cart
            </Button>
          </DialogContent>
        )}
      </Dialog>

    </Box>
  );
}
