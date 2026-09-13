(asdf:defsystem "rimefall/nucleo"
  :author "Bruno"
  :description "Simulação e conhecimento coletivo de Rimefall."
  :serial t
  :components ((:file "notas-de-campo") (:file "campo") (:file "persistencia") (:file "rimefall")))

(asdf:defsystem "rimefall"
  :author "Bruno"
  :description "Demo de sobrevivência ártica com a LWLGL."
  :version "0.2.0"
  :depends-on ("rimefall/nucleo" "lwlgl/opengl" "lwlgl/input" "lwlgl/openal")
  :serial t
  :components ((:file "apresentacao") (:file "interface"))
  :in-order-to ((asdf:test-op (asdf:test-op "rimefall/testes"))))

(asdf:defsystem "rimefall/testes"
  :author "Bruno"
  :depends-on ("rimefall/nucleo")
  :components ((:file "testes"))
  :perform (asdf:test-op (operacao sistema)
             (declare (ignore operacao sistema))
             (uiop:symbol-call :rimefall :executar-testes)))
