;;; Inicialização independente do diretório corrente e do arquivo de configuração do SBCL.
(require :asdf)
(unless (find-package :ql)
  (let ((configuracao (merge-pathnames "quicklisp/setup.lisp" (user-homedir-pathname))))
    (when (probe-file configuracao) (load configuracao))))
(asdf:load-asd (merge-pathnames "rimefall.asd" *load-truename*))
(asdf:load-system "rimefall")
(let ((argumentos (uiop:command-line-arguments)))
  (apply #'rimefall:iniciar-jogo
         (append (when (member "--validar" argumentos :test #'string=)
                   (list :validacao t :quadros-maximos 3780
                         :pasta-capturas (asdf:system-relative-pathname "rimefall" "validacao/") :sincronizar nil))
                 (when (member "--sem-audio" argumentos :test #'string=) (list :sem-audio t)))))
