import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog, filedialog
import winreg
import os
import ctypes


def get_system_env():
    env = {}
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                           r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment")
        i = 0
        while True:
            try:
                name, value, _ = winreg.EnumValue(key, i)
                env[name] = value
                i += 1
            except OSError:
                break
        winreg.CloseKey(key)
    except:
        pass
    return env


def get_user_env():
    env = {}
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment")
        i = 0
        while True:
            try:
                name, value, _ = winreg.EnumValue(key, i)
                env[name] = value
                i += 1
            except OSError:
                break
        winreg.CloseKey(key)
    except:
        pass
    return env


def set_user_env(name, value):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, name, 0, winreg.REG_EXPAND_SZ, value)
        winreg.CloseKey(key)
        os.environ[name] = value
        return True
    except Exception as e:
        messagebox.showerror("错误", f"设置失败: {str(e)}")
        return False


def set_system_env(name, value):
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                           r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                           0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, name, 0, winreg.REG_EXPAND_SZ, value)
        winreg.CloseKey(key)
        os.environ[name] = value
        return True
    except Exception as e:
        messagebox.showerror("错误", f"设置失败: {str(e)}")
        return False


def delete_user_env(name):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, name)
        winreg.CloseKey(key)
        if name in os.environ:
            del os.environ[name]
        return True
    except Exception as e:
        messagebox.showerror("错误", f"删除失败: {str(e)}")
        return False


def delete_system_env(name):
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                           r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                           0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, name)
        winreg.CloseKey(key)
        if name in os.environ:
            del os.environ[name]
        return True
    except Exception as e:
        messagebox.showerror("错误", f"删除失败: {str(e)}")
        return False


def refresh_environment():
    try:
        user_env = get_user_env()
        system_env = get_system_env()
        
        for name, value in {**user_env, **system_env}.items():
            os.environ[name] = value
            try:
                ctypes.windll.kernel32.SetEnvironmentVariableW(name, value)
            except:
                pass
        
        HWND_BROADCAST = 0xFFFF
        WM_SETTINGCHANGE = 0x001A
        SMTO_ABORTIFHUNG = 0x0002
        
        result = ctypes.c_ulong()
        SendMessageTimeoutW = ctypes.windll.user32.SendMessageTimeoutW
        SendMessageTimeoutW(
            HWND_BROADCAST,
            WM_SETTINGCHANGE,
            0,
            ctypes.c_wchar_p("Environment"),
            SMTO_ABORTIFHUNG,
            5000,
            ctypes.byref(result)
        )
        
        SendMessageTimeoutW(
            HWND_BROADCAST,
            WM_SETTINGCHANGE,
            0,
            ctypes.c_wchar_p("SYSTEM"),
            SMTO_ABORTIFHUNG,
            5000,
            ctypes.byref(result)
        )
        
        return True
    except Exception as e:
        messagebox.showerror("错误", f"刷新失败: {str(e)}")
        return False


def show_env_dialog(name, value, is_new=False, is_user=True, callback=None):
    dialog = tk.Toplevel()
    dialog.title("新建环境变量" if is_new else "编辑环境变量")
    dialog.geometry("700x350")
    dialog.transient()
    dialog.grab_set()
    dialog.resizable(False, False)
    
    main_frame = tk.Frame(dialog)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    tk.Label(main_frame, text="变量名:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
    name_entry = tk.Entry(main_frame, width=60)
    name_entry.insert(0, name)
    if not is_new:
        name_entry.config(state=tk.DISABLED)
    name_entry.grid(row=0, column=1, padx=10, pady=10, sticky=tk.EW)
    
    tk.Label(main_frame, text="变量值:").grid(row=1, column=0, sticky=tk.NW, padx=10, pady=10)
    value_text = scrolledtext.ScrolledText(main_frame, width=60, height=8, wrap=tk.WORD)
    value_text.insert("1.0", value)
    value_text.grid(row=1, column=1, padx=10, pady=10, sticky=tk.NSEW)
    
    main_frame.grid_columnconfigure(1, weight=1)
    main_frame.grid_rowconfigure(1, weight=1)
    
    def on_ok():
        new_name = name_entry.get().strip()
        new_value = value_text.get("1.0", tk.END).strip()
        if not new_name:
            messagebox.showwarning("警告", "变量名不能为空")
            return
        if is_user:
            if set_user_env(new_name, new_value):
                dialog.destroy()
                if callback:
                    callback()
        else:
            if set_system_env(new_name, new_value):
                dialog.destroy()
                if callback:
                    callback()
    
    bottom_frame = tk.Frame(dialog)
    bottom_frame.pack(fill=tk.X, padx=10, pady=(10, 10))
    tk.Button(bottom_frame, text="取消", command=dialog.destroy, width=10, relief=tk.FLAT, bg="white").pack(side=tk.RIGHT, padx=(5, 0))
    tk.Button(bottom_frame, text="确定", command=on_ok, width=10, relief=tk.FLAT, bg="white").pack(side=tk.RIGHT, padx=(5, 0))


def show_path_dialog(name, value, is_user=True, callback=None):
    dialog = tk.Toplevel()
    dialog.title("编辑环境变量")
    dialog.geometry("800x450")
    dialog.transient()
    dialog.grab_set()
    dialog.resizable(False, False)
    
    main_frame = tk.Frame(dialog)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    left_frame = tk.Frame(main_frame)
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
    
    path_list = tk.Listbox(left_frame, height=12)
    path_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    scrollbar = tk.Scrollbar(left_frame, orient=tk.VERTICAL, command=path_list.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    path_list.config(yscrollcommand=scrollbar.set)
    
    paths = value.split(";") if value else []
    for path in paths:
        if path.strip():
            path_list.insert(tk.END, path.strip())
    
    right_frame = tk.Frame(main_frame)
    right_frame.pack(side=tk.RIGHT, fill=tk.Y)
    
    def on_new():
        new_dialog = tk.Toplevel(dialog)
        new_dialog.title("新建")
        new_dialog.geometry("500x120")
        new_dialog.transient()
        new_dialog.grab_set()
        new_dialog.resizable(False, False)
        
        tk.Label(new_dialog, text="输入路径:").pack(pady=10, padx=10, anchor=tk.W)
        path_entry = tk.Entry(new_dialog, width=60)
        path_entry.pack(padx=10, pady=5, fill=tk.X)
        path_entry.focus()
        
        def on_new_ok():
            new_path = path_entry.get().strip()
            if new_path:
                path_list.insert(tk.END, new_path)
            new_dialog.destroy()
        
        btn_frame = tk.Frame(new_dialog)
        btn_frame.pack(padx=10, pady=10)
        tk.Button(btn_frame, text="取消", command=new_dialog.destroy, width=10, relief=tk.FLAT, bg="white").pack(side=tk.RIGHT, padx=(5, 0))
        tk.Button(btn_frame, text="确定", command=on_new_ok, width=10, relief=tk.FLAT, bg="white").pack(side=tk.RIGHT, padx=(5, 0))
        
        path_entry.bind("<Return>", lambda e: on_new_ok())
    
    def on_edit():
        selection = path_list.curselection()
        if selection:
            idx = selection[0]
            old_path = path_list.get(idx)
            
            edit_dialog = tk.Toplevel(dialog)
            edit_dialog.title("编辑")
            edit_dialog.geometry("500x120")
            edit_dialog.transient()
            edit_dialog.grab_set()
            edit_dialog.resizable(False, False)
            
            tk.Label(edit_dialog, text="输入路径:").pack(pady=10, padx=10, anchor=tk.W)
            path_entry = tk.Entry(edit_dialog, width=60)
            path_entry.insert(0, old_path)
            path_entry.pack(padx=10, pady=5, fill=tk.X)
            path_entry.select_range(0, tk.END)
            path_entry.focus()
            
            def on_edit_ok():
                new_path = path_entry.get().strip()
                if new_path:
                    path_list.delete(idx)
                    path_list.insert(idx, new_path)
                edit_dialog.destroy()
            
            btn_frame = tk.Frame(edit_dialog)
            btn_frame.pack(padx=10, pady=10)
            tk.Button(btn_frame, text="取消", command=edit_dialog.destroy, width=10, relief=tk.FLAT, bg="white").pack(side=tk.RIGHT, padx=(5, 0))
            tk.Button(btn_frame, text="确定", command=on_edit_ok, width=10, relief=tk.FLAT, bg="white").pack(side=tk.RIGHT, padx=(5, 0))
            
            path_entry.bind("<Return>", lambda e: on_edit_ok())
    
    def on_browse():
        folder = filedialog.askdirectory(title="选择文件夹")
        if folder:
            path_list.insert(tk.END, folder)
    
    def on_delete():
        selection = path_list.curselection()
        if selection:
            path_list.delete(selection[0])
    
    def on_move_up():
        selection = path_list.curselection()
        if selection and selection[0] > 0:
            idx = selection[0]
            item = path_list.get(idx)
            path_list.delete(idx)
            path_list.insert(idx - 1, item)
            path_list.selection_set(idx - 1)
    
    def on_move_down():
        selection = path_list.curselection()
        if selection and selection[0] < path_list.size() - 1:
            idx = selection[0]
            item = path_list.get(idx)
            path_list.delete(idx)
            path_list.insert(idx + 1, item)
            path_list.selection_set(idx + 1)
    
    def on_edit_text():
        new_paths = []
        for i in range(path_list.size()):
            new_paths.append(path_list.get(i))
        text_value = ";".join(new_paths)
        
        text_dialog = tk.Toplevel(dialog)
        text_dialog.title("编辑文本")
        text_dialog.geometry("600x300")
        text_dialog.transient()
        text_dialog.grab_set()
        
        text_widget = scrolledtext.ScrolledText(text_dialog, width=60, height=8, wrap=tk.WORD)
        text_widget.insert("1.0", text_value)
        text_widget.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        def on_text_ok():
            new_text = text_widget.get("1.0", tk.END).strip()
            path_list.delete(0, tk.END)
            for path in new_text.split(";"):
                if path.strip():
                    path_list.insert(tk.END, path.strip())
            text_dialog.destroy()
        
        btn_frame = tk.Frame(text_dialog)
        btn_frame.pack(padx=10, pady=10)
        tk.Button(btn_frame, text="取消", command=text_dialog.destroy, width=10, relief=tk.FLAT, bg="white").pack(side=tk.RIGHT, padx=(5, 0))
        tk.Button(btn_frame, text="确定", command=on_text_ok, width=10, relief=tk.FLAT, bg="white").pack(side=tk.RIGHT, padx=(5, 0))
    
    tk.Button(right_frame, text="新建", width=12, command=on_new, relief=tk.FLAT, bg="white").pack(pady=3)
    tk.Button(right_frame, text="编辑", width=12, command=on_edit, relief=tk.FLAT, bg="white").pack(pady=3)
    tk.Button(right_frame, text="浏览...", width=12, command=on_browse, relief=tk.FLAT, bg="white").pack(pady=3)
    tk.Button(right_frame, text="删除", width=12, command=on_delete, relief=tk.FLAT, bg="white").pack(pady=3)
    tk.Button(right_frame, text="上移", width=12, command=on_move_up, relief=tk.FLAT, bg="white").pack(pady=3)
    tk.Button(right_frame, text="下移", width=12, command=on_move_down, relief=tk.FLAT, bg="white").pack(pady=3)
    tk.Button(right_frame, text="编辑文本...", width=12, command=on_edit_text, relief=tk.FLAT, bg="white").pack(pady=3)
    
    path_list.bind("<Double-1>", lambda e: on_edit())
    
    def on_ok():
        new_paths = []
        for i in range(path_list.size()):
            new_paths.append(path_list.get(i))
        new_value = ";".join(new_paths)
        if is_user:
            if set_user_env(name, new_value):
                dialog.destroy()
                if callback:
                    callback()
        else:
            if set_system_env(name, new_value):
                dialog.destroy()
                if callback:
                    callback()
    
    bottom_frame = tk.Frame(dialog)
    bottom_frame.pack(fill=tk.X, padx=10, pady=(10, 10))
    tk.Button(bottom_frame, text="取消", command=dialog.destroy, width=10, relief=tk.FLAT, bg="white").pack(side=tk.RIGHT, padx=(5, 0))
    tk.Button(bottom_frame, text="确定", command=on_ok, width=10, relief=tk.FLAT, bg="white").pack(side=tk.RIGHT, padx=(5, 0))


def main():
    root = tk.Tk()
    root.title("环境变量")
    root.geometry("700x600")
    root.resizable(True, True)
    
    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    user_label_frame = tk.LabelFrame(main_frame, text="用户变量(U)", padx=5, pady=5)
    user_label_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
    
    user_tree_frame = tk.Frame(user_label_frame)
    user_tree_frame.pack(fill=tk.BOTH, expand=True)
    
    user_tree = ttk.Treeview(user_tree_frame, columns=("value",), show="tree headings", height=8)
    user_tree.heading("#0", text="变量")
    user_tree.heading("value", text="值")
    user_tree.column("#0", width=200, anchor=tk.W)
    user_tree.column("value", width=350, anchor=tk.W)
    
    user_scrollbar = ttk.Scrollbar(user_tree_frame, orient=tk.VERTICAL, command=user_tree.yview)
    user_tree.configure(yscrollcommand=user_scrollbar.set)
    
    user_tree.grid(row=0, column=0, sticky=tk.NSEW)
    user_scrollbar.grid(row=0, column=1, sticky=tk.NS)
    user_tree_frame.grid_rowconfigure(0, weight=1)
    user_tree_frame.grid_columnconfigure(0, weight=1)
    
    user_btn_frame = tk.Frame(user_label_frame)
    user_btn_frame.pack(fill=tk.X, pady=(5, 0))
    tk.Frame(user_btn_frame).pack(side=tk.LEFT, fill=tk.X, expand=True)
    btn_delete_user = tk.Button(user_btn_frame, text="删除", width=12, relief=tk.FLAT, bg="white")
    btn_delete_user.pack(side=tk.RIGHT, padx=3)
    btn_edit_user = tk.Button(user_btn_frame, text="编辑", width=12, relief=tk.FLAT, bg="white")
    btn_edit_user.pack(side=tk.RIGHT, padx=3)
    btn_new_user = tk.Button(user_btn_frame, text="新建", width=12, relief=tk.FLAT, bg="white")
    btn_new_user.pack(side=tk.RIGHT, padx=3)
    
    system_label_frame = tk.LabelFrame(main_frame, text="系统变量(S)", padx=5, pady=5)
    system_label_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
    
    system_tree_frame = tk.Frame(system_label_frame)
    system_tree_frame.pack(fill=tk.BOTH, expand=True)
    
    system_tree = ttk.Treeview(system_tree_frame, columns=("value",), show="tree headings", height=8)
    system_tree.heading("#0", text="变量")
    system_tree.heading("value", text="值")
    system_tree.column("#0", width=200, anchor=tk.W)
    system_tree.column("value", width=350, anchor=tk.W)
    
    system_scrollbar = ttk.Scrollbar(system_tree_frame, orient=tk.VERTICAL, command=system_tree.yview)
    system_tree.configure(yscrollcommand=system_scrollbar.set)
    
    system_tree.grid(row=0, column=0, sticky=tk.NSEW)
    system_scrollbar.grid(row=0, column=1, sticky=tk.NS)
    system_tree_frame.grid_rowconfigure(0, weight=1)
    system_tree_frame.grid_columnconfigure(0, weight=1)
    
    system_btn_frame = tk.Frame(system_label_frame)
    system_btn_frame.pack(fill=tk.X, pady=(5, 0))
    tk.Frame(system_btn_frame).pack(side=tk.LEFT, fill=tk.X, expand=True)
    btn_delete = tk.Button(system_btn_frame, text="删除", width=12, relief=tk.FLAT, bg="white")
    btn_delete.pack(side=tk.RIGHT, padx=3)
    btn_edit = tk.Button(system_btn_frame, text="编辑", width=12, relief=tk.FLAT, bg="white")
    btn_edit.pack(side=tk.RIGHT, padx=3)
    btn_new = tk.Button(system_btn_frame, text="新建", width=12, relief=tk.FLAT, bg="white")
    btn_new.pack(side=tk.RIGHT, padx=3)
    
    bottom_frame = tk.Frame(main_frame)
    bottom_frame.pack(fill=tk.X, padx=10, pady=(10, 10))
    
    def on_ok():
        if refresh_environment():
            refresh_user_tree()
            refresh_system_tree()
            messagebox.showinfo("成功", "环境变量已刷新\n注意：已打开的命令行窗口需要关闭后重新打开才能看到新的环境变量")
    
    tk.Button(bottom_frame, text="取消", width=10, command=root.destroy, relief=tk.FLAT, bg="white").pack(side=tk.RIGHT, padx=(5, 0))
    tk.Button(bottom_frame, text="确定并刷新", width=12, command=on_ok, relief=tk.FLAT, bg="white").pack(side=tk.RIGHT, padx=(5, 0))
    
    def refresh_user_tree():
        for item in user_tree.get_children():
            user_tree.delete(item)
        user_env = get_user_env()
        for name, value in sorted(user_env.items()):
            user_tree.insert("", tk.END, text=name, values=(value,))
    
    def refresh_system_tree():
        for item in system_tree.get_children():
            system_tree.delete(item)
        system_env = get_system_env()
        for name, value in sorted(system_env.items()):
            system_tree.insert("", tk.END, text=name, values=(value,))
    
    def on_double_click(event, tree, is_user):
        item = tree.selection()[0] if tree.selection() else None
        if item:
            name = tree.item(item, "text")
            value = tree.item(item, "values")[0] if tree.item(item, "values") else ""
            if name.upper() == "PATH":
                show_path_dialog(name, value, is_user, refresh_user_tree if is_user else refresh_system_tree)
            else:
                show_env_dialog(name, value, False, is_user, refresh_user_tree if is_user else refresh_system_tree)
    
    def on_new_user():
        show_env_dialog("", "", True, True, refresh_user_tree)
    
    def on_edit_user():
        item = user_tree.selection()[0] if user_tree.selection() else None
        if not item:
            messagebox.showwarning("警告", "请先选择一个变量")
            return
        name = user_tree.item(item, "text")
        value = user_tree.item(item, "values")[0] if user_tree.item(item, "values") else ""
        if name.upper() == "PATH":
            show_path_dialog(name, value, True, refresh_user_tree)
        else:
            show_env_dialog(name, value, False, True, refresh_user_tree)
    
    def on_delete_user():
        item = user_tree.selection()[0] if user_tree.selection() else None
        if not item:
            messagebox.showwarning("警告", "请先选择一个变量")
            return
        name = user_tree.item(item, "text")
        if messagebox.askyesno("确认", f"确定要删除变量 {name} 吗？"):
            if delete_user_env(name):
                refresh_user_tree()
    
    def on_new_system():
        show_env_dialog("", "", True, False, refresh_system_tree)
    
    def on_edit_system():
        item = system_tree.selection()[0] if system_tree.selection() else None
        if not item:
            messagebox.showwarning("警告", "请先选择一个变量")
            return
        name = system_tree.item(item, "text")
        value = system_tree.item(item, "values")[0] if system_tree.item(item, "values") else ""
        if name.upper() == "PATH":
            show_path_dialog(name, value, False, refresh_system_tree)
        else:
            show_env_dialog(name, value, False, False, refresh_system_tree)
    
    def on_delete_system():
        item = system_tree.selection()[0] if system_tree.selection() else None
        if not item:
            messagebox.showwarning("警告", "请先选择一个变量")
            return
        name = system_tree.item(item, "text")
        if messagebox.askyesno("确认", f"确定要删除变量 {name} 吗？"):
            if delete_system_env(name):
                refresh_system_tree()
    
    btn_new_user.config(command=on_new_user)
    btn_edit_user.config(command=on_edit_user)
    btn_delete_user.config(command=on_delete_user)
    btn_new.config(command=on_new_system)
    btn_edit.config(command=on_edit_system)
    btn_delete.config(command=on_delete_system)
    
    system_env = get_system_env()
    for name, value in sorted(system_env.items()):
        system_tree.insert("", tk.END, text=name, values=(value,))
    
    user_env = get_user_env()
    for name, value in sorted(user_env.items()):
        user_tree.insert("", tk.END, text=name, values=(value,))
    
    system_tree.bind("<Double-1>", lambda e: on_double_click(e, system_tree, False))
    user_tree.bind("<Double-1>", lambda e: on_double_click(e, user_tree, True))
    
    root.mainloop()


if __name__ == "__main__":
    main()
