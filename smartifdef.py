# -*- coding: utf-8 -*-
import datetime
import sublime, sublime_plugin

#if _GNU

#elif __ANDROID__

#else

#endif


class SmartIfDefCommand(sublime_plugin.TextCommand):
    def _find_def(self, line):
        '''
        find pair of ifdef ... endif or ifdef ... else or ifdef ... elif,
        and return the Region between ifdef and endif/else/elif.
        '''
        start1 = end1 = line.end()
        i = 0
        while True:
            i += 1
            end = self.view.find(r'#else|#endif|#elif|#ifdef|#if', line.b)
            if end is None:
                 end1 = start1
                 break
            rlast_line = self.view.lines(end)[-1]
            last_line = self.view.substr(rlast_line)
            # print("fidn def last line %r" % last_line)
            if "#endif" in last_line or "#else" in last_line or "#elif" in last_line:
                end1 = end.end()
                break

            if "#if" in last_line:
                inner = self._find_endif(rlast_line)
                line = inner

            if i > 10:
                # print("inner more")
                break

        # print("find def %r " % (self.view.substr(sublime.Region(start1, end1))))
        return sublime.Region(start1, end1)

    def _find_endif(self, line):
        '''
            find 
        '''
        start1 = end1 = line.end()
        bg = self.view.find(r'#else', line.begin())
        if bg is not None:
            start1 = end1 = bg.end()

        i = 0
        while True:
            i += 1
            end = self.view.find(r'#endif|#if', line.end())
            if end is None:
                 end1 = start1
                 break
            rlast_line = self.view.lines(end)[-1]
            last_line = self.view.substr(rlast_line)
            if "#endif" in last_line:
                end1 = end.end()
                break

            if "#if" in last_line:
                inner = self._find_endif(rlast_line)
                line = inner
            if i > 10:
                print("inner more2")
                break

        # print("find endif %r %r" % (start1, end1))
        return sublime.Region(start1, end1)

    def _find_ndef(self, line):
        rdef = self._find_def(line)
        pstart = pend = rdef.end()
        rend = self._find_endif(rdef)
        pend = rend.end()
        return rend

    def __init__(self, *args, **kwargs):
        super(SmartIfDefCommand, self).__init__(*args, **kwargs)
        settings = sublime.load_settings('smartifdef.sublime-settings')
        self.defined_tags = settings.get('cppmode.defined_tags', ['__ANDROID__'])
        self.not_defined_tags = settings.get('cppmode.not_defined_tags', ['_WIN32'])
        # print("get defined_tags %r %r" % (self.defined_tags, self.not_defined_tags))


    def run(self, edit):
        content = self.view.substr(self.view.visible_region())
        text_point = self.view.text_point(1, 0)
        cur_line = self.view.full_line(text_point)
        line_text = self.view.substr(cur_line)

        ignore_regions = []
        regs = self.view.find_all(r'#if|#elif')
        for reg in regs:
            l = self.view.full_line(reg)
            ltxt = self.view.substr(l)
            # print("get line %s" % ltxt)

            for tag in self.defined_tags:
                if tag in ltxt:
                    # print("defined tags %r" % (ltxt))
                    if 'ifndef' in ltxt:
                        ignore_regions.append(self._find_def(l))
                    elif 'elif' in ltxt:
                        ignore_regions.append(self._find_ndef(l))
                    else:
                        ignore_regions.append(self._find_ndef(l))

            for tag in self.not_defined_tags:
                if tag in ltxt:
                    # print("not defined tags %r" % (ltxt))
                    if 'ifndef' in ltxt:
                        ignore_regions.append(self._find_ndef(l))
                    elif 'elif' in ltxt:
                        ignore_regions.append(self._find_def(l))
                    else:
                        ignore_regions.append(self._find_def(l))

        # print("text %r" % line_text)
        self.view.add_regions('ifdef', ignore_regions, 'comment', 'circle', sublime.DRAW_NO_OUTLINE)
