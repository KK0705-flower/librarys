const video = document.querySelector('#js-video');
const resultDiv = document.querySelector('#result');

// Quaggaの初期設定
Quagga.init({
    inputStream: {
        name: "Live",
        type: "LiveStream",
        target: video, // video要素をターゲットにする
        constraints: {
            facingMode: "environment" // 背面カメラ
        },
    },
    decoder: {
        readers: ["ean_reader"] // 
    }
}, function(err) {
    if (err) {
        console.error(err);
        resultDiv.innerText = "エラー: カメラを起動できません";
        return;
    }
    Quagga.start();
});

// バーコードを検知した時の処理
Quagga.onDetected(function(data) {
    const code = data.codeResult.code;
    
    // 日本の本のISBNは通常「978」から始まります
    if (code.startsWith("978")) {
        resultDiv.innerText = "読み取り成功: " + code;
        resultDiv.style.background = "#ccffcc";
        
        // 【重要】ここで取得したISBNを使って、本の情報を検索する処理へ飛ばす
        // window.location.href = "/add_book/?isbn=" + code;
        
        // 連続読み取りを防ぐために一時停止
        Quagga.stop();
        setTimeout(() => { Quagga.start(); }, 3000); 
    }
});

// スキャンで読み取った時
Quagga.onDetected(function(data) {
    const code = data.codeResult.code;
    processISBN(code); // 共通の処理へ
});

// 手入力ボタンを押した時
document.querySelector('#search-btn').addEventListener('click', () => {
    const code = document.querySelector('#isbn-input').value;
    processISBN(code); // 共通の処理へ
});

// 共通処理：ISBNを使って本の情報を探す
function processISBN(isbn) {
    
    if (isbn.length < 10) {
        alert("正しいISBNを入力してください");
        return;
    }
    console.log("処理中のISBN:", isbn);
    // ここでDjangoのViewへリダイレクト、あるいはAPIを叩く
   window.location.href = `/book_register/?isbn=${isbn}`;
}