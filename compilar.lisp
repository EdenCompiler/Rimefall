;;; Gera um executável Linux com a imagem do SBCL e copia os modelos necessários.
(require :asdf)
(unless (find-package :ql)
  (let ((configuracao (merge-pathnames "quicklisp/setup.lisp" (user-homedir-pathname))))
    (when (probe-file configuracao) (load configuracao))))
(asdf:load-asd (merge-pathnames "rimefall.asd" *load-truename*))
(asdf:load-system "rimefall")
(asdf:test-system "rimefall/testes")

(defun rimefall::iniciar-executavel ()
  (handler-case
      (let* ((pasta (uiop:pathname-directory-pathname sb-ext:*runtime-pathname*))
             (rimefall::*pasta-modelos* (merge-pathnames "modelos/" pasta))
             (argumentos (rest sb-ext:*posix-argv*)))
        (apply #'rimefall:iniciar-jogo
               (append (when (member "--validar" argumentos :test #'string=)
                         (list :validacao t :quadros-maximos 3780 :sincronizar nil
                               :pasta-capturas (merge-pathnames "validacao/" pasta)))
                       (when (member "--sem-audio" argumentos :test #'string=) (list :sem-audio t)))))
    (error (condicao)
      (format *error-output* "~&Não foi possível executar Rimefall: ~A~%" condicao)
      (sb-ext:exit :code 1))))

(let* ((pasta (asdf:system-relative-pathname "rimefall" "distribuicao/"))
       (destino (merge-pathnames "rimefall" pasta)))
  (ensure-directories-exist (merge-pathnames "modelos/" pasta))
  (dolist (origem (directory (merge-pathnames (make-pathname :name :wild :type "malha")
                                             (asdf:system-relative-pathname "rimefall" "modelos/"))))
    (uiop:copy-file origem (merge-pathnames (file-namestring origem) (merge-pathnames "modelos/" pasta))))
  (uiop:copy-file (asdf:system-relative-pathname "rimefall" "README.md") (merge-pathnames "README.md" pasta))
  (format t "~&Gravando executável em ~A~%" destino)
  (sb-ext:save-lisp-and-die (namestring destino) :toplevel #'rimefall::iniciar-executavel
                           :executable t :compression t :save-runtime-options t))
