// static/js/baseThree.js
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

/**
 * Three.jsの初期化関数
 */
export function initThree(canvasId, cameraKey = "cameraPosition") {
  const canvas = document.getElementById(canvasId);
  const scene = new THREE.Scene();

  const camera = new THREE.PerspectiveCamera(75, canvas.clientWidth / canvas.clientHeight, 0.1, 100);
  const savedPos = sessionStorage.getItem(cameraKey);
  if (savedPos) {
    const { x, y, z } = JSON.parse(savedPos);
    camera.position.set(x, y, z);
  } else {
    camera.position.set(0, 0, 3);
  }

  window.addEventListener("beforeunload", () => {
    const pos = camera.position;
    sessionStorage.setItem(cameraKey, JSON.stringify({ x: pos.x, y: pos.y, z: pos.z }));
  });

  const renderer = new THREE.WebGLRenderer({
    canvas: canvas,
    preserveDrawingBuffer: true
  });

  renderer.setClearColor(0xE88A10, 1);
  renderer.setPixelRatio(window.devicePixelRatio || 1);
  renderer.setSize(canvas.clientWidth, canvas.clientHeight);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;

  // 補助オブジェクト
  scene.add(new THREE.AxesHelper(20));
  scene.add(new THREE.GridHelper(20, 10));

  return { canvas, scene, camera, renderer, controls };
}


