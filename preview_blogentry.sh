 #!/bin/zsh

warn_and_exit()
{
    cat <<EOF

This script provides a quick preview of the current blog entry in your
local browser.

You have to adopt this script to your settings (paths, synchronization
tool) in order to run properly.

Therefore, I stop here until you modified this script to meet your
requirements.

EOF
    exit 1
    }

## check for host name and show warning when not my own host:
[ "x${HOSTNAME}" = "xsherri" ] || warn_and_exit



cd ~/src/lazyblorg
rm -rf testdata/2del/*
mkdir testdata/2del/blog

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
    --blogname "public voit" \
    --aboutblog "public voit" \
    --targetdir testdata/2del/blog \
    --previous-metadata nonexisting-preview-metadata.pk \
    --new-metadata testdata/2del/blog/preview-metadata.pk \
    --logfile testdata/2del/errors.org \
    --orgfiles ./testdata/about-placeholder.org ./templates/blog-format.org \
    /tmp/lazyblorg-preview.org && \
find testdata/2del -name '*.html' -exec xdg-open "{}" \;

#end
