// d:\work\dev\fastapi\hadbit-fastapi\static\js\htmx_toast.js

/**
 * トースト通知を表示する汎用関数
 * @param {string} message - 表示するメッセージ
 * @param {string} type - 'success', 'error', 'info' のいずれか
 */
function showToast(message, type = 'success') {
  const toast = document.createElement("div");
  toast.className = "toast toast-top toast-end z-50";

  let alertClass = 'alert-success';
  let icon = 'fa-check-circle';

  if (type === 'error') {
    alertClass = 'alert-error';
    icon = 'fa-exclamation-circle';
  } else if (type === 'info') {
    alertClass = 'alert-info';
    icon = 'fa-info-circle';
  }

  toast.innerHTML = `
    <div class="alert ${alertClass} text-white shadow-lg">
      <i class="fa-solid ${icon}"></i>
      <span>${message}</span>
    </div>`;
  document.body.appendChild(toast);

  // トースト内のHTMX属性（hx-getなど）を有効化
  // DOM追加直後だと認識されない場合があるため、わずかに遅延させる
  setTimeout(() => {
    const htmxObj = window.htmx || (typeof htmx !== 'undefined' ? htmx : null);
    if (htmxObj) {
      htmxObj.process(toast);
    }
  }, 10);

  // 5秒後にトーストを削除
  setTimeout(() => toast.remove(), 5000);
}

// htmxのリクエスト完了イベントを監視
document.body.addEventListener("htmx:afterRequest", function (evt) {
  const xhr = evt.detail.xhr;
  // requestConfigからパスを取得（より確実）
  const path = evt.detail.requestConfig ? evt.detail.requestConfig.path : xhr.responseURL;
  
  // HTMXが判定した成功フラグ (2xx系ならtrue)
  const isSuccess = evt.detail.successful;

  // 1. サーバー側から HX-Trigger ヘッダーでトースト指示が来た場合を優先して処理
  const hxTrigger = xhr.getResponseHeader("HX-Trigger");
  if (hxTrigger) {
    try {
      const triggers = JSON.parse(hxTrigger);
      if (triggers.toast) {
        const t = triggers.toast;
        // 文字列ならメッセージとして、オブジェクトなら詳細指定として扱う
        showToast(t.message || t, t.type || 'success');
        return;
      }
    } catch (e) {
      // JSONパースエラー時は無視（単純なイベントトリガーの可能性）
    }
  }

  // 2. パスベースのデフォルト動作（サーバーからの指定がない場合）
  if (isSuccess) {
    if (path && path.includes("/api/hadbit/records/create")) {
      showToast("登録しました");
    }
  } else {
    // ネットワークエラー(status=0)は htmx:sendError で扱うため除外
    if (xhr.status > 0) {
      showToast(`エラーが発生しました (${xhr.status})`, 'error');
    }
  }
});

// ネットワークエラー（サーバーに到達できない場合など）の監視
document.body.addEventListener("htmx:sendError", function (evt) {
  showToast("通信エラーが発生しました", 'error');
});
