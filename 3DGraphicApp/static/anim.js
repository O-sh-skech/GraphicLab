import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js"; 


  const canvas = document.getElementById("three-canvas");
  const scene = new THREE.Scene();

  const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 100);
  camera.position.set(0, 0, 3);

  const renderer = new THREE.WebGLRenderer({ canvas });
  renderer.setClearColor(0x000000, 0); // 背景を透明に
  renderer.setSize(canvas.clientWidth, canvas.clientHeight);

  // カメラ操作
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;

  

  // 補助オブジェクト
  scene.add(new THREE.AxesHelper(20));
  scene.add(new THREE.GridHelper(20, 10));

  // 球体
  const sphere = new THREE.Mesh(
    new THREE.SphereGeometry(0.1, 16, 16),
    new THREE.MeshStandardMaterial({ color: 0x00ff00 })
  );
  scene.add(sphere);

  // ライト
  const light = new THREE.DirectionalLight(0xffffff, 1);
  light.position.set(1, 1, 1);
  scene.add(light);

  fetch("static/Json/animation.json")
    .then(response => {
      if (!response.ok) {
        alert("JSONの読み込みに失敗しました");
      }
      return response.json();
    })
    .then(data => {
      const rawArray = data;
      const path = [];

      for (let i = 0; i < rawArray.length; i += 7) {
        const x = rawArray[i];
        const y = rawArray[i + 1];
        const z = rawArray[i + 2];
        path.push(new THREE.Vector3(x, y, z));
      }

    // 処理が成功したので不要ファイルを削除するfetchをここで実行する
    fetch('/delete-file?name=static/Json/animation.json', { method: 'DELETE' })
    .then(res => {
      if (!res.ok) console.warn('ファイル削除失敗');
    })
    .catch(err => console.error('削除時のエラー:', err));
    

        let currentIndex = 0;
        let trailPoints = [];
        let trailLine = null;
        const speed = 1.2;


        function animate() {
        requestAnimationFrame(animate);

        const target = path[currentIndex];
        const current = sphere.position;

        const dx = target.x - current.x;
        const dy = target.y - current.y;
        const dz = target.z - current.z;
        const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);

        if (dist < 0.01) {
          trailPoints.push(current.clone());
          currentIndex = (currentIndex + 1) % path.length;
        } else {
          current.x += dx * speed;
          current.y += dy * speed;
          current.z += dz * speed;
          trailPoints.push(current.clone());
        }

        updateLine();
        renderer.render(scene, camera);
        }

        function updateLine() {
            if (trailLine) {
            scene.remove(trailLine);
            }

        const geometry = new THREE.BufferGeometry().setFromPoints(trailPoints);
        const material = new THREE.LineBasicMaterial({ color: 0xff0000 });
        trailLine = new THREE.Line(geometry, material);
        scene.add(trailLine);
        }

        animate();

        window.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
         window.location.href = "/";  // Flaskでdraw.htmlを返すルートにしておく
        }
        });

      window.addEventListener("resize", () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
      });
    })
    .catch(err => {
      console.error("エラー:", err);
    });