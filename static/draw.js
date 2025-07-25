import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";


// Canvas取得と基本設定
const canvas = document.getElementById("three-canvas");
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(
  75, window.innerWidth / window.innerHeight, 0.1, 1000
);
const savedPos = sessionStorage.getItem("cameraPosition1");

if (savedPos) {
  const { x, y, z } = JSON.parse(savedPos);
  camera.position.set(x, y, z);
} else {
  camera.position.set(0, 0, 3); // 初回は初期位置
}
//カメラ位置の保存
window.addEventListener("beforeunload", () => {
  const pos = camera.position;
  sessionStorage.setItem("cameraPosition0", JSON.stringify({ x: pos.x, y: pos.y, z: pos.z }));
});

const renderer = new THREE.WebGLRenderer({ canvas });
renderer.setClearColor(0x000000, 0); // 背景を透明に
renderer.setSize(canvas.clientWidth, canvas.clientHeight);

// カメラ操作
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

// 補助オブジェクト
scene.add(new THREE.AxesHelper(20));
scene.add(new THREE.GridHelper(20, 10));



// fetchでJSONデータ読み込み
let i = 0;

async function loadMeshes() {
  while (true) {
    const pointPath = `/static/Json/points_${i}.json`;
    const texPath = `/static/Json/texCoords_${i}.json`;
    const facePath = `/static/Json/faces_${i}.json`;

    try {
      const [pointsRes, texCoordsRes, facesRes] = await Promise.all([
        fetch(pointPath),
        fetch(texPath),
        fetch(facePath)
      ]);

      // いずれかのファイルが存在しなければ終了
      if (!pointsRes.ok || !texCoordsRes.ok || !facesRes.ok){
        console.warn("失敗")
        break;
      }

      const [pointsData, texCoordsData, facesData] = await Promise.all([
        pointsRes.json(),
        texCoordsRes.json(),
        facesRes.json()
      ]);

      



      const geometry = new THREE.BufferGeometry();
      const vertices = new Float32Array(pointsData);
      const uvs = new Float32Array(texCoordsData);
      const indices = new Uint16Array(facesData);

      geometry.setAttribute("position", new THREE.BufferAttribute(vertices, 3));
      geometry.setAttribute("uv", new THREE.BufferAttribute(uvs, 2));
      geometry.setIndex(new THREE.BufferAttribute(indices, 1));
      geometry.computeVertexNormals();

      const material = new THREE.MeshStandardMaterial({
        color: 0x00ff00,
        side: THREE.DoubleSide
      });

      const triangleMesh = new THREE.Mesh(geometry, material);
      scene.add(triangleMesh);

      i++; // 次の番号へ

    } catch (err) {
      alert(`読み込み中にエラー（${i}番目）: ${err.message || err}`);
      break;
    }
  }
}

loadMeshes();


// 光源
const light = new THREE.DirectionalLight(0xffffff, 1.5);
light.position.set(1, 1, 1);
scene.add(light);

// レンダリングループ
    function animate() {
      requestAnimationFrame(animate);
      controls.update();  // 操作の反映（enableDamping有効なら必須）
      renderer.render(scene, camera);
    }

    animate();