// layout.js - 统一处理 PC 和手机交互
export default function registerInteractions(app) {
  let longPressTimer = null;
  let isDragging = false;
  let startX = 0, startY = 0;
  let initialDistance = 0;
  let isZooming = false;
  let zoomEndTimer = null;

  const emitEvent = (type, detail = {}) => {
    const event = new CustomEvent("interaction", { 
      detail: { 
        type,
        source: detail.source || 'mouse', // 'mouse' 或 'touch'
        ...detail 
      } 
    });
    window.dispatchEvent(event);
  };

  const getDistance = (touch1, touch2) =>
    Math.hypot(touch2.clientX - touch1.clientX, touch2.clientY - touch1.clientY);

  // -------- 通用事件处理 --------
  const handleDragStart = (x, y, source) => {
    isDragging = true;
    startX = x;
    startY = y;
    emitEvent("dragStart", { x, y, source });
  };

  const handleDragMove = (x, y, source) => {
    if (isDragging) {
      emitEvent("dragMove", { 
        x, 
        y,
        deltaX: x - startX,
        deltaY: y - startY,
        source 
      });
    }
  };

  const handleDragEnd = (x, y, source) => {
    if (isDragging) {
      isDragging = false;
      emitEvent("dragEnd", { 
        x, 
        y,
        deltaX: x - startX,
        deltaY: y - startY,
        source 
      });
    }
  };

  const handleZoom = (delta, center, source, additionalProps = {}) => {
    emitEvent("zoom", {
      delta,
      center,
      ratio: window.devicePixelRatio,
      source,
      ...additionalProps
    });
  };

  // -------- PC事件 --------
  window.addEventListener("contextmenu", e => {
    e.preventDefault();
    emitEvent("rightClick", { x: e.clientX, y: e.clientY, source: 'mouse' });
  });

  window.addEventListener("mousedown", e => {
    if (e.button === 0) {
      handleDragStart(e.clientX, e.clientY, 'mouse');
    }
  });

  window.addEventListener("mousemove", e => {
    handleDragMove(e.clientX, e.clientY, 'mouse');
  });

  window.addEventListener("mouseup", e => {
    handleDragEnd(e.clientX, e.clientY, 'mouse');
  });

  window.addEventListener("wheel", e => {
    if (e.ctrlKey) {
      e.preventDefault();
      const delta = e.deltaY > 0 ? -0.1 : 0.1;
      handleZoom(delta, { x: e.clientX, y: e.clientY }, 'wheel', {
        wheelDelta: e.deltaY
      });
    }
  }, { passive: false });

  // -------- 手机事件 --------
  window.addEventListener("touchstart", e => {
    if (e.touches.length === 1) {
      const t = e.touches[0];
      startX = t.clientX;
      startY = t.clientY;

      longPressTimer = setTimeout(() => {
        emitEvent("rightClick", { x: startX, y: startY, source: 'touch' });
      }, 500);

      // 立即开始拖动
      handleDragStart(t.clientX, t.clientY, 'touch');

    } else if (e.touches.length === 2) {
      clearTimeout(longPressTimer);
      isZooming = true;
      const [t1, t2] = e.touches;
      initialDistance = getDistance(t1, t2);
      emitEvent("zoomStart", {
        distance: initialDistance,
        center: { x: (t1.clientX + t2.clientX)/2, y: (t1.clientY + t2.clientY)/2 },
        source: 'touch'
      });
    }
  }, { passive: false });

  window.addEventListener("touchmove", e => {
    if (e.touches.length === 1 && !isZooming) {
      clearTimeout(longPressTimer);
      const t = e.touches[0];
      handleDragMove(t.clientX, t.clientY, 'touch');

    } else if (e.touches.length === 2) {
      const [t1, t2] = e.touches;
      const currentDistance = getDistance(t1, t2);
      const scale = currentDistance / initialDistance;
      const delta = (scale - 1) * 0.5; // 平滑缩放因子

      handleZoom(delta, { 
        x: (t1.clientX + t2.clientX)/2, 
        y: (t1.clientY + t2.clientY)/2 
      }, 'touch', {
        scale,
        distance: currentDistance
      });

      if (zoomEndTimer) clearTimeout(zoomEndTimer);
      zoomEndTimer = setTimeout(() => {
        emitEvent("zoomEnd", { 
          finalScale: scale, 
          source: 'touch' 
        });
        isZooming = false;
      }, 150);
    }
  }, { passive: false });

  window.addEventListener("touchend", e => {
    clearTimeout(longPressTimer);

    if (e.touches.length === 0) {
      if (isZooming) {
        emitEvent("zoomEnd", { source: 'touch' });
        isZooming = false;
      } else {
        const t = e.changedTouches[0];
        handleDragEnd(t.clientX, t.clientY, 'touch');
      }
    } else if (e.touches.length === 1 && isZooming) {
      isZooming = false;
      emitEvent("zoomEnd", { source: 'touch' });
    }
  }, { passive: false });

  // 视口变化监听
  if (window.visualViewport) {
    window.visualViewport.addEventListener('resize', () => {
      emitEvent("viewportChange", {
        width: window.visualViewport.width,
        height: window.visualViewport.height,
        scale: window.visualViewport.scale,
        offsetLeft: window.visualViewport.offsetLeft,
        offsetTop: window.visualViewport.offsetTop,
        source: 'viewport'
      });
    });
  }

  // -------- 视口变化统一封装 --------
  // 1) window resize / orientationchange
  ['resize', 'orientationchange'].forEach(evt =>
    window.addEventListener(evt, () =>
      emitEvent('viewportChange', {
        width: window.innerWidth,
        height: window.innerHeight,
        source: evt        // 方便调试
      })
    )
  );
  
  // 2) Visual Viewport API
  if (window.visualViewport) {
    window.visualViewport.addEventListener('resize', () =>
      emitEvent('viewportChange', {
        width: window.visualViewport.width,
        height: window.visualViewport.height,
        scale: window.visualViewport.scale,
        offsetLeft: window.visualViewport.offsetLeft,
        offsetTop: window.visualViewport.offsetTop,
        source: 'visualViewport'
      })
    );
  }

}