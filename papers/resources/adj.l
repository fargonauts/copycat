(defun get-temperature-adjusted-probability (prob &aux low-prob-factor
						       result)
; This function is a filter:  it inputs a value (from 0 to 100) and returns
; a probability (from 0 - 1) based on that value and the temperature.  When
; the temperature is 0, the result is (/ value 100), but at higher 
; temperatures, values below 50 get raised and values above 50 get lowered
; as a function of temperature.
; I think this whole formula could probably be simplified.

  (setq result
	(cond ((= prob 0) 0)
	      ((<= prob .5)
               (setq low-prob-factor (max 1 (truncate (abs (log prob 10)))))
               (min (+ prob 
		       (* (/ (- 10 (sqrt (fake-reciprocal *temperature*))) 
			     100) 
			  (- (expt 10 (- (1- low-prob-factor))) prob)))
		    .5))
		     
   	      ((= prob .5) .5)
	      ((> prob .5)
               (max (- 1
		        (+ (- 1 prob) 
		           (* (/ (- 10 (sqrt (fake-reciprocal *temperature*))) 
			         100)
			      (- 1 (- 1 prob)))))
	            .5))))
  result)
