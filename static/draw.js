import { initThree } from "./base.js";
import * as THREE from "three";

const { canvas, scene, camera, renderer, controls } = initThree("three-canvas", "cameraPosition0");

// Three.js のレンダラーと canvas サイズを同期させる
const resizeCanvas = () => {
  const width = window.innerWidth * 0.8;  // 80vw 相当
  const height = window.innerHeight * 0.6; // 60vh 相当

  canvas.width = width;
  canvas.height = height;

  renderer.setSize(width, height);
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
};

// 最初の描画時
resizeCanvas();

// ウィンドウサイズ変更時にも対応
window.addEventListener('resize', resizeCanvas);

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