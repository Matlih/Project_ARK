import React, { useRef, useMemo, Component, Suspense } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Html, useTexture } from '@react-three/drei';
import { EffectComposer, Bloom } from '@react-three/postprocessing';
import * as THREE from 'three';
import { useArkStore } from '../../store/arkStore';
import { useShallow } from 'zustand/react/shallow';

// --- MATH UTILITIES ---
// Converts Geographic Coordinates to 3D Cartesian space on a sphere
const getSpherePosition = (lat, lon, radius) => {
  const phi = (90 - lat) * (Math.PI / 180);
  const theta = (lon + 180) * (Math.PI / 180);
  
  const x = -(radius * Math.sin(phi) * Math.cos(theta));
  const z = (radius * Math.sin(phi) * Math.sin(theta));
  const y = (radius * Math.cos(phi));
  
  return new THREE.Vector3(x, y, z);
};

// --- HOLOGRAPHIC PIN COMPONENT ---
const HologramPin = ({ lat, lon, label }) => {
  const groupRef = useRef();
  const ringRef = useRef();
  
  // Calculate exact 3D position on the sphere
  const position = useMemo(() => getSpherePosition(lat, lon, 2.0), [lat, lon]);

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();
    
    // Animate the radar ring pulsing
    if (ringRef.current) {
      ringRef.current.scale.setScalar(1 + Math.sin(t * 4) * 0.3);
      ringRef.current.material.opacity = 0.6 - Math.sin(t * 4) * 0.4;
    }
    
    // Orient the entire pin assembly to point directly away from the Earth's core
    if (groupRef.current) {
      groupRef.current.lookAt(0, 0, 0);
    }
  });

  return (
    <group ref={groupRef} position={position}>
      
      {/* 1. Base Core (The anchor point) */}
      <mesh>
        <sphereGeometry args={[0.015, 16, 16]} />
        <meshBasicMaterial color="#F43F5E" />
      </mesh>

      {/* 2. Animated Radar Ring */}
      {/* Rotated to lay flat against the surface */}
      <mesh ref={ringRef} rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[0.05, 0.003, 16, 32]} />
        <meshBasicMaterial color="#F43F5E" transparent opacity={0.8} />
      </mesh>

      {/* 3. Vertical Laser Beam */}
      {/* In lookAt(0,0,0) space, negative Z points outward toward space */}
      <mesh position={[0, 0, -0.1]} rotation={[Math.PI / 2, 0, 0]}>
        <cylinderGeometry args={[0.002, 0.002, 0.2, 8]} />
        <meshBasicMaterial color="#F43F5E" transparent opacity={0.6} blending={THREE.AdditiveBlending} />
      </mesh>

      {/* 4. Attached UI Label */}
      {/* Pinned to the top of the laser beam so it never drifts */}
      <Html position={[0, 0, -0.25]} center zIndexRange={[100, 0]}>
        <div className="flex flex-col items-center pointer-events-none select-none animate-in fade-in zoom-in duration-500">
          <div className="text-rose-400 text-[9px] font-bold tracking-widest font-mono border border-rose-500/40 px-2 py-0.5 bg-[#0B101E]/90 backdrop-blur-md whitespace-nowrap shadow-[0_0_10px_rgba(244,63,94,0.2)]">
            {label || "ECONOMIC IMPACT ZONE"}
          </div>
          <div className="w-px h-4 bg-gradient-to-b from-rose-500/80 to-transparent my-1"></div>
        </div>
      </Html>
    </group>
  );
};

// --- CORE GLOBE COMPONENT ---
const Globe = () => {
  const globeRef = useRef();
  const { camera } = useThree();

  // NEW: Load the alpha mask from the public folder
  const alphaMask = useTexture('/earth-alpha-mask.png');

  // Architectural Rule: useShallow strictly limits re-renders
  const { globeTarget, damageZones } = useArkStore(
    useShallow((state) => ({
      globeTarget: state.globeTarget,
      damageZones: state.damageZones,
      pipelineStatus: state.pipelineStatus 
    }))
  );

  // Calculate target camera vector whenever globeTarget changes
  const targetCameraPos = useMemo(() => {
    if (!globeTarget) return new THREE.Vector3(0, 0, 6); // Default backout position
    const pos = getSpherePosition(globeTarget.lat, globeTarget.lon, 2.0);
    return new THREE.Vector3(pos.x * 3, pos.y * 3, pos.z * 3); // Zoom multiplier
  }, [globeTarget]);

  // Calculate HTML label position
  const labelPos = useMemo(() => {
    if (!globeTarget) return null;
    return getSpherePosition(globeTarget.lat, globeTarget.lon, 2.0);
  }, [globeTarget]);

  useFrame((state, delta) => {
    // ONLY force the camera to move if we have an active target lock
    if (globeTarget) {
      camera.position.lerp(targetCameraPos, 0.05);
      camera.lookAt(0, 0, 0); // Keep focused on the center while zooming
    }
    // If there is no target, we do nothing! We let OrbitControls handle the mouse.
  });

  return (
    <group ref={globeRef}>
      
      {/* 1. HOLOGRAPHIC LANDMASSES */}
      {/* Note: Adjust the middle number (Y-axis) to slide the map East/West */}
      <mesh rotation={[0, 0.22, 0]}> 
        <sphereGeometry args={[1.98, 64, 64]} />
        <meshBasicMaterial 
          color="#22d3ee"           
          transparent={true}        
          alphaMap={alphaMask}      
          opacity={0.85}            
          blending={THREE.AdditiveBlending} 
          depthWrite={false}        
        />
      </mesh>

      {/* 2. INNER ENERGY CORE */}
      <mesh scale={0.98}>
        <sphereGeometry args={[1.98, 32, 32]} />
        <meshBasicMaterial 
          color="#0B101E"           
          transparent={true}
          opacity={0.4}
          wireframe={true}          
          blending={THREE.AdditiveBlending}
        />
      </mesh>

      {/* 3. NEW HOLOGRAPHIC PINS */}
      {/* If the system is targeting a zone, render the pin */}
      {globeTarget && (
        <HologramPin 
          lat={globeTarget.lat} 
          lon={globeTarget.lon} 
          label={globeTarget.label} 
        />
      )}
      
      {/* Note: We removed the old floating <Html> block entirely! */}
      
    </group>
  );
};

// --- ERROR BOUNDARY (FALLBACK STRATEGY) ---
class GlobeErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("[ARK Architecture] 3D Globe Critical Failure:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="w-full h-full bg-[#0B0F19] flex items-center justify-center relative overflow-hidden border border-rose-500/20">
          <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none z-10">
            <p className="text-rose-500 font-mono text-sm bg-black/50 px-3 py-1 border border-rose-500/50">
              3D CONTEXT UNAVAILABLE
            </p>
            <p className="text-[#94A3B8] font-mono text-xs mt-2">
              2D Fallback Active. System functionality unimpaired.
            </p>
          </div>
          <img 
            src="/ph_outline.png" 
            alt="Fallback Philippine Map" 
            className="w-auto h-3/4 opacity-20 object-contain"
            onError={(e) => e.target.style.display = 'none'} 
          />
        </div>
      );
    }

    return this.props.children;
  }
}

// --- CANVAS WRAPPER (DEFAULT EXPORT) ---
const ARKGlobe = () => {
  // Pull the target state so the controls know when an event is happening
  const globeTarget = useArkStore((state) => state.globeTarget);

  return (
    <GlobeErrorBoundary>
      <div className="w-full h-full bg-[#0B0F19] relative">
        <Canvas
          className="w-full h-full"
          camera={{ position: [0, 0, 6], fov: 45 }}
          gl={{ antialias: true, alpha: true }}
          dpr={[1, 2]}
        >
          <ambientLight intensity={0.3} />
          
          <Suspense fallback={null}>
            <Globe />
          </Suspense>
          
          <EffectComposer>
            <Bloom 
              luminanceThreshold={0.1} 
              luminanceSmoothing={0.9} 
              intensity={1.5} 
            />
          </EffectComposer>
          
          {/* UPGRADED CONTROLS */}
          <OrbitControls 
            enableZoom={false} 
            enablePan={false} 
            enableRotate={!globeTarget} // Locks user rotation when targeting an event
            autoRotate={!globeTarget}   // Auto-rotates ONLY when idle
            autoRotateSpeed={0.8}       // The speed of the idle rotation
          />
        </Canvas>
      </div>
    </GlobeErrorBoundary>
  );
};

export default ARKGlobe;