(require :asdf)
(asdf:load-asd (merge-pathnames "rimefall.asd" *load-truename*))
(asdf:test-system "rimefall/testes")
