;! clipleft=0 cliptop=0 clipwidth=39 clipheight=40
*loop
; 1
	@clip left=0 top=0
	@wait time=300
; 2
	@clip left=0 top=40
	@wait time=300
; 3
	@clip left=0 top=80
	@wait time=300
@jump target=*loop
