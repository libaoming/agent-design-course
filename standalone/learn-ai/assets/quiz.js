/* ============================================================
   可复用测验组件 — 检索练习（retrieval practice）
   用法：在 HTML 里写
   <div class="quiz" data-answer="1"
        data-ok="答对的反馈" data-no="答错的反馈">
     <div class="quiz-q">问题文字</div>
     <button class="quiz-opt">选项 A</button>
     <button class="quiz-opt">选项 B</button>
     <button class="quiz-opt">选项 C</button>
     <div class="quiz-fb"></div>
   </div>
   data-answer = 正确选项的 0-based 下标。
   点击即时反馈，作答后锁定。这就是「尽可能紧」的反馈环。
   ============================================================ */
(function () {
  function initQuiz(quiz) {
    var answer = parseInt(quiz.getAttribute('data-answer'), 10);
    var okMsg = quiz.getAttribute('data-ok') || '正确。';
    var noMsg = quiz.getAttribute('data-no') || '再想想。';
    var opts = Array.prototype.slice.call(quiz.querySelectorAll('.quiz-opt'));
    var fb = quiz.querySelector('.quiz-fb');
    var answered = false;

    opts.forEach(function (opt, i) {
      opt.addEventListener('click', function () {
        if (answered) return;
        answered = true;
        opts.forEach(function (o, j) {
          o.disabled = true;
          if (j === answer) o.classList.add('correct');
        });
        if (i === answer) {
          fb.textContent = '✓ ' + okMsg;
          fb.className = 'quiz-fb show ok';
        } else {
          opt.classList.add('wrong');
          fb.textContent = '✗ ' + noMsg;
          fb.className = 'quiz-fb show no';
        }
      });
    });
  }
  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.quiz').forEach(initQuiz);
  });
})();
