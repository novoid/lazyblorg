#!/bin/zsh
cd ~/src/lazyblorg
rm -rf testdata/2del/*

## This script provides a quick preview of the current blog entry in your local browser.
## You will need a LISP function similar to the one below:
##
##    (defun my-lazyblorg-test()
## 	"Saves current blog entry to file and invoke lazyblorg process with it"
## 	(interactive)
## 	(save-excursion
## 	  (search-backward ":blog:");; search begin of current (previous) blog entry
## 	  (beginning-of-line nil)
## 	  (set-mark-command nil);; set mark
## 	  (org-cycle);; close org-mode heading and sub-headings
## 	  (next-line);; goto next org-mode heading (this should be next line after blog entry)
## 	  (beginning-of-line nil)
## 	  (let ((p (point));; copy region
## 		(m (mark)))
## 	    (if (< p m)
## 		(kill-ring-save p m)
## 	      (kill-ring-save m p)))
## 	  (find-file "/tmp/lazyblorg-preview.org");; hard coded temporary file (will be overwritten)
## 	  (erase-buffer);; I told you!
## 	  (yank);; paste region from above
## 	  (save-buffer);; save to disk
## 	  (kill-buffer "lazyblorg-preview.org");; destroy last evidence
## 	  (previous-line);;
## 	  (org-cycle);; close org-mode heading and sub-headings
## 	  ;; invoke lazyblorg:
## 	  (shell-command-to-string "/home/vk/src/lazyblorg/preview_blogentry.sh");; invoke shell script
## 	  )
## 	)

PYTHONPATH="~/src/lazyblorg:" ./lazyblorg.py \
    --quiet \
    --aboutblog "public voit" \
    --targetdir testdata/2del \
    --previous-metadata nonexisting-preview-metadata.pk \
    --new-metadata testdata/2del/blog/preview-metadata.pk \
    --logfile testdata/2del/errors.org \
    --orgfiles ./templates/blog-format.org \
    /tmp/lazyblorg-preview.org && \
find testdata/2del -name '*.html' -exec xdg-open "{}" \;
               
#end
