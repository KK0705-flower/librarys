
// ページが完全に準備できてからカメラを起動する
const startCamera = async () => {
    const video = document.querySelector('#js-video');
    
    if (!video) {
        console.error("エラー: #js-video が見つかりません。");
        return;
    }

    try {
        // exact: 'environment' を外し、背面カメラを「推奨」する設定に変更
        const stream = await navigator.mediaDevices.getUserMedia({
            audio: false,
            video: {
                facingMode: "environment" 
            }
        });
        
        video.srcObject = stream;
        // ブラウザの制限を回避するため、明示的にplayを呼ぶ
        await video.play();
        console.log("カメラ起動成功");
        
    } catch (err) {
        console.error("カメラエラー:", err);
        alert("カメラを起動できませんでした。ブラウザの『カメラ許可』がオフになっているか、HTTPS通信ではない可能性があります。");
    }
};

// DOMの読み込み完了を待ってから実行
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', startCamera);
} else {
    startCamera();
}

