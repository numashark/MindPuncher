// Web版のランキングに使うFirebaseの設定（Firebaseコンソールの「プロジェクトの設定」→「マイアプリ」の値を入れる）
// databaseURL が空のままならランキングはブラウザ（localStorage）に保存する
// recaptchaSiteKey はApp Checkに登録したreCAPTCHA v3のサイトキー。空ならApp Checkを使わない
window.mindPuncherFirebase = {
  apiKey: "",
  authDomain: "",
  databaseURL: "",
  projectId: "",
  appId: "",
  recaptchaSiteKey: "",
};
