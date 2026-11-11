// Web版のランキングに使うFirebaseの設定（Firebaseコンソールの「プロジェクトの設定」→「マイアプリ」の値を入れる）
// databaseURL が空のままならランキングはブラウザ（localStorage）に保存する
// measurementId はGoogleアナリティクスの測定ID（G-で始まる）。空なら起動ページの閲覧を計測しない
// recaptchaSiteKey はApp Checkに登録したFraud Defense（旧称 reCAPTCHA Enterprise）のサイトキー。空ならApp Checkを使わない
window.mindPuncherFirebase = {
  apiKey: "AIzaSyDtOhoZuU7lXR74xSTnmRB_VCEhxe9A_0A",
  authDomain: "mind-puncher.firebaseapp.com",
  databaseURL: "https://mind-puncher-default-rtdb.firebaseio.com",
  projectId: "mind-puncher",
  appId: "1:758491651569:web:463b3a3506f4b0bb2ab850",
  measurementId: "",
  recaptchaSiteKey: "6Lcy9hUuAAAAAOzvg8FtupTmCFDpCWGesZtoBOZX",
};
