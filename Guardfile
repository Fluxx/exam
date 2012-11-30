guard :shell do
    watch(/^(tests|exam)(.*)\.py$/) do |match|
        puts `python setup.py nosetests`
    end
end
