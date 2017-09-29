import math

class Temperature(object):
    def __init__(self):
        self.reset()

    def reset(self):
        self.actual_value = 100.0
        self.last_unclamped_value = 100.0
        self.clamped = True
        self.clampTime = 30

    def update(self, value):
        self.last_unclamped_value = value
        if self.clamped:
            self.actual_value = 100.0
        else:
            self.actual_value = value

    def clampUntil(self, when):
        self.clamped = True
        self.clampTime = when
        # but do not modify self.actual_value until someone calls update()

    def tryUnclamp(self, currentTime):
        if self.clamped and currentTime >= self.clampTime:
            self.clamped = False

    def value(self):
        return 100.0 if self.clamped else self.actual_value

    def getAdjustedValue(self, value):
        return value ** (((100.0 - self.value()) / 30.0) + 0.5)

    """
    def getAdjustedProbability(self, value):
        if value == 0 or value == 0.5 or self.value() == 0:
            return value
        if value < 0.5:
            return 1.0 - self.getAdjustedProbability(1.0 - value)
        coldness = 100.0 - self.value()
        a = math.sqrt(coldness)
        c = (10 - a) / 100
        f = (c + 1) * value
        return max(f, 0.5)
    """

    def getAdjustedProbability(self, value):
        # TODO: use entropy 

        """
        This function returns the probability for a decision.
        Copied above.

        Please look at the last line of it.  Strangely, it was
        return max(f, 0.5).  Does that make sense? Let's compare
        some results.  Where it was (0.5), we obtained, for example:

        iiijjjlll: 670 (avg time 1108.5, avg temp 23.6)
        iiijjjd: 2 (avg time 1156.0, avg temp 35.0)
        iiijjjkkl: 315 (avg time 1194.4, avg temp 35.5)
        iiijjjkll: 8 (avg time 2096.8, avg temp 44.1)
        iiijjjkkd: 5 (avg time 837.2, avg temp 48.0)

        wyz: 5 (avg time 2275.2, avg temp 14.9)
        xyd: 982 (avg time 2794.4, avg temp 17.5)
        yyz: 7 (avg time 2731.9, avg temp 25.1)
        dyz: 2 (avg time 3320.0, avg temp 27.1)
        xyy: 2 (avg time 4084.5, avg temp 31.1)
        xyz: 2 (avg time 1873.5, avg temp 52.1)

        Now, let's see what return max(f, 0.0000) does:

        wyz: 7 (avg time 3192.9, avg temp 13.1)
        xyd: 985 (avg time 2849.1, avg temp 17.5)
        yyz: 6 (avg time 3836.7, avg temp 18.6)
        xyy: 1 (avg time 1421.0, avg temp 19.5)
        xyz: 1 (avg time 7350.0, avg temp 48.3)

        They *seem* better (in the strict sense that we've obtained both
        lower T and more times of wyz.)  But they're *not* statistically
        significant (for 1000 runs).

        Now... looking at the code... it seems to be a mess... what does
        function f() even mean in intuitive terms?

        Work it does, but dude... quite a hack.

        Another run, with return f @line89:

        wyz: 8 (avg time 4140.5, avg temp 13.3)
        yyz: 6 (avg time 2905.2, avg temp 14.5)
        xyd: 982 (avg time 3025.4, avg temp 17.6)
        dyz: 4 (avg time 4265.0, avg temp 17.7)

        Does it even matter? Another (quick) run, I think with return (0.5):

        dyz: 1 (avg time 5198.0, avg temp 15.3)
        wyz: 3 (avg time 4043.7, avg temp 17.1)
        yyz: 9 (avg time 3373.6, avg temp 21.0)
        xyd: 84 (avg time 5011.1, avg temp 23.3)
        xyy: 3 (avg time 4752.0, avg temp 27.9)

        Compared to return(0.99):

        xyd: 1000 (avg time 1625.2, avg temp 17.3)

        Comparing to return f --> Statistically significant.
        Comparing to return(0.5) --> same, so this return value does something.

        Now running return(0.0):

        xyz: 3 (avg time 3996.7, avg temp 81.1)
        dyz: 46 (avg time 5931.7, avg temp 82.6)
        xd: 17 (avg time 6090.3, avg temp 83.8)
        xyd: 934 (avg time 7699.8, avg temp 88.1)

        It's bad overall, but at least it's statistically significant!

        return (-f * (math.log2(f))) # Entropy test #1 (global).

        wyz: 123 (avg time 5933.1, avg temp 16.5)
        xyy: 200 (avg time 6486.7, avg temp 27.8)
        yyz: 330 (avg time 6310.2, avg temp 38.5)
        dyz: 75 (avg time 6393.3, avg temp 39.6)
        yzz: 5 (avg time 4965.0, avg temp 59.3)
        xyz: 160 (avg time 6886.2, avg temp 60.2)
        xd: 4 (avg time 2841.0, avg temp 61.8)
        dz: 3 (avg time 3721.0, avg temp 62.1)
        xyd: 100 (avg time 5853.1, avg temp 67.5)

        Here we get an intuitive result: entropy/uncertainty seems better at
        exploring a whole range of possible solutions.  It even seems, at least
        to me, better than the distribution obtained by the original copycat.

        instead of log2, trying ln --> return (-f * math.log(f)):

        wyz: 78 (avg time 7793.7, avg temp 16.6)
        xyy: 202 (avg time 9168.5, avg temp 27.5)
        wxz: 1 (avg time 3154.0, avg temp 33.4)
        dyz: 63 (avg time 7950.3, avg temp 41.7)
        yyz: 217 (avg time 8147.4, avg temp 41.7)
        xyz: 201 (avg time 7579.7, avg temp 62.5)
        xxy: 1 (avg time 7994.0, avg temp 64.8)
        yzz: 8 (avg time 4672.6, avg temp 65.7)
        xd: 9 (avg time 9215.2, avg temp 68.1)
        xyd: 217 (avg time 7677.9, avg temp 73.8)
        dz: 3 (avg time 20379.0, avg temp 77.3)

        (quickly) trying out (1-this_entropy_function):

        xyd: 100 (avg time 2984.3, avg temp 18.2)

        And that's beautiful! One wants an inverse function that punishes
        exploration and creativity, that takes all the fluidity off
        the system.

        But somehow this completely messes up with abc abd iijjkk:

        jijjkk: 66 (avg time 3200.1, avg temp 61.3)
        iijjkk: 114 (avg time 5017.2, avg temp 63.5)
        dijjkk: 23 (avg time 2209.0, avg temp 67.3)
        iijjkl: 748 (avg time 3262.8, avg temp 70.0)
        iijjkd: 49 (avg time 2315.9, avg temp 76.3)

        Which leads me to suspect that someone may have overfitted the
        model for either xyz or iijjkk or some other problem, and one
        improvement there means disaster here.

        Something tells me to invert again to 1-entropy... and bingo!

        iijjll: 59 (avg time 797.4, avg temp 19.8)
        iijjkl: 41 (avg time 696.1, avg temp 28.5)

        My guess is that some code is prefering to find groups in the
        opposite form that it likes finding the "symmetry/opposite"
        concepts of the xyz problem.

        Sould compare & contrast the unhappiness and relevance of both
        the opposite/symmetry codelets and the grouping/chunking codelets.
        My hunch is the sameness group code: something there that
        interacts with Temperature is wicked, and should be relatively
        easy to find the error.

        Here's why:  the following run was done on (1-entropy(f)):

        mrrlll: 77 (avg time 2195.7, avg temp 41.4)
        mrrd: 2 (avg time 1698.0, avg temp 42.6)
        mrrkkl: 20 (avg time 1317.8, avg temp 46.6)
        mrrkkd: 1 (avg time 1835.0, avg temp 48.6)


        If (1-entropy(f)) binds the system into a tight corridor of possibilities,
        then why does it easily get the samenessGroup right?  If this is right,
        then running just entropy(f) should have big trouble with samenessGroup.
        Let's see:

        nrrkkk: 11 (avg time 3637.8, avg temp 64.6)
        drrkkk: 3 (avg time 5921.3, avg temp 66.2)
        mrrkkd: 7 (avg time 6771.3, avg temp 74.6)
        mrrkkl: 79 (avg time 3723.0, avg temp 74.9)

        So there we are: the system is unable to find that change samenessGroup
        to next letterCategory, so there ought to be something very different
        in the code that:

        * Interacts with Temperature (things like unhappiness, relevance, depth,
        urgency, and whatever else interacts with T)
        * something very close to samenessGroup... sameGroup, sameness,
        sameNeighbors, etc... is encoded in a form that is *directly opposite*
        to other concepts/categories/codlets, etc.  


        Need to play with this more... and WTF is f anyways?

        LSaldyt:

        Recall self.value():
        def value(self):
            return 100.0 if self.clamped else self.actual_value
        
        f in terms of value() and value only
        f = ((10 - sqrt(100 - self.value()))/100 + 1) * value
        so, the function: (10 - sqrt(100 - temp)) / 100 
        produces a scalar from the current temperature,
        ranging from 1.0 when the temp is 0 to 1.1 when the temp is 100.
        This is used to scale probablities in their inverse directions

        For the original LISP program:
            ; This function is a filter:  it inputs a value (from 0 to 100) and returns
            ; a probability (from 0 - 1) based on that value and the temperature. 
            *********************************************************
            ; When the temperature is 0, the result is (/ value 100), but at higher 
            ; temperatures, values below 50 get raised and values above 50 get lowered
            ; as a function of temperature.
            **********************************************************
            ; I think this whole formula could probably be simplified.
            **********************************************************

            (defun get-temperature-adjusted-probability (prob &aux low-prob-factor
                                                                   result)
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

        Which was tested using:

            (defun test-get-temperature-adjusted-probability (prob)
            (with-open-file (ostream "testfile" :direction :output 
                                              :if-does-not-exist :create
                                              :if-exists :append) 
                    (format ostream "prob: ~a~&" prob)
              (loop for temp in '(0 10 20 30 40 50 60 70 80 90 100) do
                    (setq *temperature* temp)
                    (format ostream "Temperature: ~a; probability ~a~&"
                            temp (float (get-temperature-adjusted-probability prob))))
              (format ostream "~%")))

        Interpretation:

        Importantly, the values of .5 in both the min and max correspond to the mid-cutoff of 50:
            i.e. 'values below 50 get raised and values above 50 get lowered'
        Still, it is interesting to note that changing 'return max(f, 0.0) to max(f, 0.5) has no significant effect on the distribution

        It looks like the function below preserves most of the functionality of the original lisp.
        However, the comments themselves agree that the formula is overly complicated.

        """
        prob = value # Slightly more descriptive (and less ambiguous), will change argument
        # Temperature, potentially clamped
        temp = self.value()
        iprob = 1 - prob

        
        # This function does precisely what I think the original lisp comment describes, but provides crappy results
        # return (temp / 200) * iprob + ((200 - temp) / 200) * prob
        # However, this version preforms much better:
        # Some statistical analysis is needed of course
        return (temp / 100) * iprob + ((100 - temp) / 100) * prob
        '''
        lucas@infinity:~/projects/personal/copycat$ ./main.py abc abd xyz --iterations 10 --plot
        Answered wyz (time 3865, final temperature 13.9)
        Answered wyz (time 8462, final temperature 10.8)
        Answered wyz (time 6062, final temperature 11.7)
        Answered yyz (time 4022, final temperature 15.6)
        Answered yyz (time 2349, final temperature 59.8)
        Answered xyd (time 17977, final temperature 14.9)
        Answered xyd (time 1550, final temperature 14.7)
        Answered xyd (time 11755, final temperature 16.8)
        Answered wyz (time 2251, final temperature 13.7)
        Answered yyz (time 13007, final temperature 11.7)
        wyz: 4 (avg time 5160.0, avg temp 12.5)
        xyd: 3 (avg time 10427.3, avg temp 15.5)
        yyz: 3 (avg time 6459.3, avg temp 29.0)

        However, it generally does worse on abc:abd::ijjkk:_

        lucas@infinity:~/projects/personal/copycat$ ./main.py abc abd ijjkkk --iterations 10 --plot
        Answered ijjlll (time 7127, final temperature 17.6)
        Answered ijjlll (time 968, final temperature 17.5)
        Answered ijjkkl (time 1471, final temperature 19.8)
        Answered ijjlll (time 1058, final temperature 13.2)
        Answered ijjkkl (time 489, final temperature 83.9)
        Answered ijjkkl (time 1576, final temperature 18.7)
        Answered ijjkkl (time 1143, final temperature 65.2)
        Answered ijjkkl (time 3067, final temperature 19.6)
        Answered ijjkkl (time 1973, final temperature 40.4)
        Answered ijjkkl (time 1064, final temperature 50.6)
        ijjlll: 3 (avg time 3051.0, avg temp 16.1)
        ijjkkl: 7 (avg time 1540.4, avg temp 42.6)
        '''
        # unparameterized version
        #curvedProb = (temp / 100) * iprob + (cold / 100) * prob

        #if prob < .5:
        #    # Curving small (<.5) probabilities to .5, but not over
        #    return max(curvedProb, .5)
        #else:
        #    # Curving large (>.5) probabilities to .5, but not under
        #    return min(curvedProb, .5)

        # parameterized version : weights towards or away from probabilities
        # alpha = 1.0
        # beta  = 1.0
        # return ((alpha + temp / 100) * iprob +  (beta + cold / 100) * prob) / (alpha + beta)

        '''
        # A scaling factor (between 0 and infinity), based on temperature (i.e. 100/coldness)
        if temp == 100: # Avoid dividing by zero
            factor = float('inf') 
        else:
            # My factor:
            # factor = 100 / (100 - temp)
            # SQRT:
            # factor = math.sqrt(100 / (100 - temp))
            # Original factor:
            # factor = (110 - math.sqrt(100 - temp)) / 100
            # Factor ^ 10:
            # factor = ((110 - math.sqrt(100 - temp)) / 100) ** 10.
            # Factor ^ 20
            # factor = ((110 - math.sqrt(100 - temp)) / 100) ** 20.
            # No factor:
            # factor = 1
        if prob == .5:
            return .5
        elif prob > .5:
            prob = prob / factor
        elif prob < .5:
            prob = prob * factor
        return min(max(prob, 0), 1) # Normalize between 0 and 1.
        
        if value == 0 or value == 0.5 or self.value() == 0:
            return value
        if value < 0.5:
            return 1.0 - self.getAdjustedProbability(1.0 - value)
        coldness = 100.0 - self.value()
        a = math.sqrt(coldness)
        c = (10 - a) / 100
        f = (c + 1) * value
        # return max(f, 0.5)
        # return max(f, 0.0)
        # return (0 + (-f * math.log2(f)))
        return -f * math.log2(f)
        '''
